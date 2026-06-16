"""Module 22 — Settings & Admin"""
import streamlit as st
import pandas as pd
from db import get_supabase
from config import (MAROON, GOLD, CREAM, COLLEGE_NAME, ACADEMIC_YEAR,
                    DEPARTMENTS, PROGRAMMES, MODULES)

ROLES = ["admin","counselor","staff","viewer"]


def load_users(sb):
    try:
        return sb.table("users").select("*").order("created_at").execute().data or []
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>⚙️ Settings & Admin</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            System configuration, user management, and integrations.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_general, tab_users, tab_db, tab_integrations = st.tabs(
        ["🏫 General", "👥 Users", "🗄️ Database", "🔌 Integrations"])

    # ── General ───────────────────────────────────────────────
    with tab_general:
        st.subheader("College Information")
        st.markdown(f"**College Name:** {COLLEGE_NAME}")
        st.markdown(f"**Academic Year:** {ACADEMIC_YEAR}")
        st.markdown(f"**Supabase URL:** Connected ✅")
        st.divider()

        st.subheader("Module Registry")
        st.markdown(f"**Total Modules:** {len(MODULES)}")
        mod_df = pd.DataFrame(MODULES, columns=["Name","Icon","File","Section"])
        mod_df["File"] = mod_df["File"].apply(lambda f: f"modules/{f}.py")
        st.dataframe(mod_df[["Section","Name","Icon","File"]],
                     use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Departments & Programmes")
        dc1, dc2 = st.columns(2)
        dc1.markdown("**Departments:** " + " · ".join(DEPARTMENTS))
        dc2.markdown("**Programmes:** " + " · ".join(PROGRAMMES))

    # ── User management ───────────────────────────────────────
    with tab_users:
        users = load_users(sb)
        st.subheader(f"Users ({len(users)})")

        if users:
            df = pd.DataFrame(users)[["full_name","email","role","is_active","created_at"]]
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d %b %Y")
            df.columns = ["Name","Email","Role","Active","Created"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No users yet. Add your first user below.")

        st.divider()
        st.subheader("Add User")
        with st.form("add_user_form", clear_on_submit=True):
            uc1, uc2 = st.columns(2)
            u_name  = uc1.text_input("Full Name *")
            u_email = uc2.text_input("Email *")
            uc3, uc4 = st.columns(2)
            u_role   = uc3.selectbox("Role", ROLES)
            u_active = uc4.checkbox("Active", value=True)

            if st.form_submit_button("➕ Add User", type="primary"):
                if not u_name.strip() or not u_email.strip():
                    st.error("Name and Email are required.")
                else:
                    try:
                        sb.table("users").insert({
                            "full_name": u_name.strip(),
                            "email":     u_email.strip(),
                            "role":      u_role,
                            "is_active": u_active,
                        }).execute()
                        st.success(f"✅ User {u_name} added as {u_role}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")

    # ── Database ──────────────────────────────────────────────
    with tab_db:
        st.subheader("Live Table Counts")
        tables = {
            "applicants":         "👤 Applicants",
            "applications":       "📝 Applications",
            "counseling_sessions":"🗣️ Sessions",
            "follow_ups":         "🔔 Follow-ups",
            "users":              "👥 Users",
        }
        cols = st.columns(len(tables))
        for col, (tbl, label) in zip(cols, tables.items()):
            try:
                count = sb.table(tbl).select("id", count="exact").execute().count or 0
            except:
                count = "—"
            with col:
                st.markdown(
                    f"<div class='metric-card'><h3>{count}</h3><p>{label}</p></div>",
                    unsafe_allow_html=True)

        st.divider()
        st.subheader("Danger Zone")
        st.error("⚠️ These actions are irreversible. Use with caution.")
        with st.expander("🗑️ Clear Test Data"):
            st.warning("This will delete ALL applicants and related records where "
                       "full_name contains 'Test' or 'test'.")
            if st.button("Delete Test Records", type="secondary"):
                try:
                    sb.table("applicants").delete()\
                        .ilike("full_name", "%test%").execute()
                    st.success("Test records deleted.")
                except Exception as e:
                    st.error(f"Failed: {e}")

    # ── Integrations ──────────────────────────────────────────
    with tab_integrations:
        st.subheader("Integration Status")

        integrations = [
            ("Supabase (Database)",  True,  "Connected — data stored at agfmeefnfzsrpyzwejtt.supabase.co"),
            ("SMS Gateway (MSG91)",  False, "Not configured — add API key below"),
            ("WhatsApp (Twilio)",    False, "Not configured"),
            ("Email (SMTP/SendGrid)",False, "Not configured"),
            ("Google Calendar",      False, "Not configured"),
        ]
        for name, connected, note in integrations:
            status = "✅ Connected" if connected else "❌ Not Connected"
            color  = "#27AE60" if connected else "#E74C3C"
            st.markdown(
                f"<div style='border:1px solid {color};border-radius:8px;"
                f"padding:10px 14px;margin:6px 0;'>"
                f"<b>{name}</b> &nbsp; <span style='color:{color};'>{status}</span><br>"
                f"<small style='color:#666;'>{note}</small></div>",
                unsafe_allow_html=True
            )

        st.divider()
        st.subheader("Add SMS API Key")
        with st.form("sms_config"):
            provider = st.selectbox("Provider", ["MSG91","2Factor","Twilio","Other"])
            api_key  = st.text_input("API Key", type="password")
            sender   = st.text_input("Sender ID / From Number")
            if st.form_submit_button("Save API Config"):
                st.info("API key storage not yet implemented — "
                        "add keys to .streamlit/secrets.toml and restart the app.")

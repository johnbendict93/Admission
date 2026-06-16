"""Module 07 — Applicant Profiles (full profile view + edit)"""
import streamlit as st
import pandas as pd
from datetime import date
from db import get_supabase
from config import (MAROON, GOLD, CREAM, DEPARTMENTS, PROGRAMMES,
                    CATEGORIES, LEAD_SOURCES, APPLICANT_STATUSES)

GENDERS   = ["Male", "Female", "Other"]
BLOOD_GRP = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

STATUS_COLORS = {
    "New Lead": "#3498DB", "Contacted": "#9B59B6", "Interested": "#27AE60",
    "Documents Pending": "#E67E22", "Documents Submitted": "#F39C12",
    "Counseled": "#1ABC9C", "Confirmed": "#2ECC71", "Fee Paid": "#16A085",
    "Enrolled": "#8B1A1A", "Not Interested": "#95A5A6", "Dropped": "#E74C3C",
}


def load_list(sb, search="", status_filter=None, dept_filter=None):
    q = sb.table("applicants").select(
        "id, reg_number, full_name, mobile, programme_interested, "
        "department_interested, status, created_at"
    ).order("created_at", desc=True)
    if status_filter:
        q = q.in_("status", status_filter)
    if dept_filter:
        q = q.in_("department_interested", dept_filter)
    try:
        rows = q.execute().data or []
        df = pd.DataFrame(rows)
        if not df.empty and search:
            s = search.lower()
            df = df[
                df["full_name"].str.lower().str.contains(s, na=False) |
                df["mobile"].str.contains(s, na=False) |
                df["reg_number"].str.lower().str.contains(s, na=False)
            ]
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()


def load_full(sb, applicant_id):
    try:
        rows = sb.table("applicants").select("*").eq("id", applicant_id).execute().data
        return rows[0] if rows else {}
    except:
        return {}


def load_sessions(sb, applicant_id):
    try:
        rows = sb.table("counseling_sessions").select(
            "id, session_date, session_type, outcome, next_action, created_at"
        ).eq("applicant_id", applicant_id).order("created_at", desc=True).execute().data or []
        return rows
    except:
        return []


def load_followups(sb, applicant_id):
    try:
        rows = sb.table("follow_ups").select(
            "id, title, due_date, priority, status"
        ).eq("applicant_id", applicant_id).order("due_date").execute().data or []
        return rows
    except:
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>👤 Applicant Profiles</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Search and view full applicant profiles. Click any row to open the profile.
        </p>
    </div>""", unsafe_allow_html=True)

    # ── List / Search pane ────────────────────────────────────
    col_list, col_profile = st.columns([1, 2])

    with col_list:
        search = st.text_input("🔎 Search", placeholder="Name / Mobile / Reg No")
        f_status = st.multiselect("Status", APPLICANT_STATUSES, key="ap_status")
        f_dept   = st.multiselect("Dept",   DEPARTMENTS,        key="ap_dept")

        df = load_list(sb, search, f_status or None, f_dept or None)
        st.markdown(f"**{len(df)} applicant(s)**")

        if df.empty:
            st.info("No applicants found.")
            selected_id = None
        else:
            # Build selection list
            options = {
                f"{r['reg_number']} — {r['full_name']}": r["id"]
                for _, r in df.iterrows()
            }
            chosen_label = st.radio("Select applicant", list(options.keys()),
                                     label_visibility="collapsed")
            selected_id = options.get(chosen_label)

    # ── Profile pane ──────────────────────────────────────────
    with col_profile:
        if not selected_id:
            st.markdown("""<div class="module-placeholder">
                <p>Select an applicant on the left to view their full profile.</p>
            </div>""", unsafe_allow_html=True)
            return

        p = load_full(sb, selected_id)
        if not p:
            st.error("Could not load profile.")
            return

        status = p.get("status", "")
        sc = STATUS_COLORS.get(status, "#888")
        st.markdown(f"""
        <div style='background:{CREAM};border-radius:10px;padding:16px 20px;
             border-left:5px solid {MAROON};margin-bottom:12px;'>
            <h3 style='margin:0;color:{MAROON};'>{p.get('full_name','—')}</h3>
            <span style='background:{sc};color:#fff;padding:2px 10px;
                  border-radius:12px;font-size:0.8rem;'>{status}</span>
            &nbsp;<small style='color:#555;'>{p.get('reg_number','')}</small>
        </div>""", unsafe_allow_html=True)

        tab_info, tab_edit, tab_history = st.tabs(
            ["📄 Info", "✏️ Edit Profile", "🗒️ Activity"])

        # ── Info tab ──────────────────────────────────────────
        with tab_info:
            c1, c2 = st.columns(2)
            def field(col, label, key):
                val = p.get(key) or "—"
                col.markdown(f"**{label}:** {val}")

            field(c1, "Mobile",      "mobile")
            field(c2, "Email",       "email")
            field(c1, "Gender",      "gender")
            field(c2, "DOB",         "dob")
            field(c1, "Blood Group", "blood_group")
            field(c2, "Category",    "category")
            st.divider()
            field(c1, "Father",      "father_name")
            field(c2, "Father Mob",  "father_mobile")
            field(c1, "Mother",      "mother_name")
            field(c2, "School",      "school_name")
            field(c1, "HSC %",       "hsc_percentage")
            field(c2, "Lead Source", "lead_source")
            st.divider()
            field(c1, "Programme",   "programme_interested")
            field(c2, "Department",  "department_interested")
            if p.get("address"):
                st.markdown(f"**Address:** {p['address']}")
            if p.get("notes"):
                st.markdown("**Notes:**")
                st.code(p["notes"], language=None)

        # ── Edit tab ──────────────────────────────────────────
        with tab_edit:
            with st.form("edit_profile"):
                ec1, ec2 = st.columns(2)
                new_name   = ec1.text_input("Full Name", p.get("full_name",""))
                new_mobile = ec2.text_input("Mobile",    p.get("mobile",""))
                new_email  = ec1.text_input("Email",     p.get("email","") or "")
                new_gender = ec2.selectbox("Gender", [""]+GENDERS,
                    index=([""]+GENDERS).index(p.get("gender","")) if p.get("gender") in GENDERS else 0)
                new_prog   = ec1.selectbox("Programme", [""]+PROGRAMMES,
                    index=([""]+PROGRAMMES).index(p.get("programme_interested",""))
                    if p.get("programme_interested") in PROGRAMMES else 0)
                new_dept   = ec2.selectbox("Department", [""]+DEPARTMENTS,
                    index=([""]+DEPARTMENTS).index(p.get("department_interested",""))
                    if p.get("department_interested") in DEPARTMENTS else 0)
                new_status = ec1.selectbox("Status", APPLICANT_STATUSES,
                    index=APPLICANT_STATUSES.index(status) if status in APPLICANT_STATUSES else 0)
                new_cat    = ec2.selectbox("Category", [""]+CATEGORIES,
                    index=([""]+CATEGORIES).index(p.get("category",""))
                    if p.get("category") in CATEGORIES else 0)
                new_notes  = st.text_area("Notes", p.get("notes","") or "", height=80)

                if st.form_submit_button("💾 Save Changes", type="primary"):
                    payload = {
                        "full_name":              new_name.strip(),
                        "mobile":                 new_mobile.strip(),
                        "email":                  new_email.strip() or None,
                        "gender":                 new_gender or None,
                        "programme_interested":   new_prog or None,
                        "department_interested":  new_dept or None,
                        "status":                 new_status,
                        "category":               new_cat or None,
                        "notes":                  new_notes.strip() or None,
                    }
                    try:
                        sb.table("applicants").update(payload).eq("id", selected_id).execute()
                        st.success("✅ Profile updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")

        # ── Activity tab ──────────────────────────────────────
        with tab_history:
            sessions = load_sessions(sb, selected_id)
            followups = load_followups(sb, selected_id)

            st.markdown("**Counseling Sessions**")
            if sessions:
                for s in sessions:
                    st.markdown(
                        f"📅 `{s.get('session_date','—')}` &nbsp; "
                        f"**{s.get('session_type','—')}** &nbsp; → &nbsp; "
                        f"{s.get('outcome','—')}"
                    )
                    if s.get("next_action"):
                        st.caption(f"Next: {s['next_action']}")
            else:
                st.info("No counseling sessions recorded.")

            st.divider()
            st.markdown("**Follow-ups**")
            priority_icon = {"Urgent":"🔴","High":"🟠","Normal":"🟡","Low":"🟢"}
            if followups:
                for f in followups:
                    icon = priority_icon.get(f.get("priority",""), "⚪")
                    st.markdown(
                        f"{icon} **{f['title']}** — Due: `{f.get('due_date','—')[:10]}` "
                        f"— Status: `{f.get('status','—')}`"
                    )
            else:
                st.info("No follow-ups recorded.")

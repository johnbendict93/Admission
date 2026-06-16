"""Module 10 — Counseling Sessions"""
import streamlit as st
import pandas as pd
from datetime import date
from db import get_lookup, get_supabase
from config import MAROON, GOLD, CREAM



def load_applicants(sb):
    try:
        rows = sb.table("applicants").select("id, reg_number, full_name, mobile")\
            .not_.in_("status", ["Dropped","Not Interested"])\
            .order("full_name").execute().data or []
        return {f"{r['reg_number']} — {r['full_name']}": r for r in rows}
    except:
        return {}


def load_sessions(sb, applicant_id=None):
    try:
        q = sb.table("counseling_sessions").select(
            "id, applicant_id, session_date, session_type, "
            "outcome, next_action, duration_mins, created_at, "
            "applicants(reg_number, full_name)"
        ).order("session_date", desc=True).limit(50)
        if applicant_id:
            q = q.eq("applicant_id", applicant_id)
        return q.execute().data or []
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🗣️ Counseling Sessions</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Log and review all counseling interactions.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_log, tab_history = st.tabs(["➕ Log New Session", "📋 Session History"])

    applicants = load_applicants(sb)

    # ── Log new session ───────────────────────────────────────
    with tab_log:
        if not applicants:
            st.info("No active applicants. Register some walk-ins first.")
        else:
            with st.form("session_form", clear_on_submit=True):
                st.subheader("Log Counseling Session")
                chosen = st.selectbox("Applicant *", list(applicants.keys()))
                applicant = applicants[chosen]

                c1, c2, c3 = st.columns(3)
                session_date = c1.date_input("Session Date *", value=date.today())
                session_type = c2.selectbox("Session Type *", get_lookup("session_type"))
                duration     = c3.number_input("Duration (mins)", min_value=5,
                                                max_value=240, value=30, step=5)
                outcome      = st.selectbox("Outcome *", get_lookup("session_outcome"))
                next_action  = st.text_input("Next Action",
                    placeholder="e.g. Send fee structure, call after 2 days")
                remarks      = st.text_area("Session Notes", height=80,
                    placeholder="Key discussion points, concerns raised…")

                submitted = st.form_submit_button("💾 Save Session",
                                                   type="primary",
                                                   use_container_width=True)

            if submitted:
                payload = {
                    "applicant_id":   applicant["id"],
                    "session_date":   session_date.isoformat(),
                    "session_type":   session_type,
                    "outcome":        outcome,
                    "next_action":    next_action.strip() or None,
                    "duration_mins":  int(duration),
                    "notes":          remarks.strip() or None,
                }
                try:
                    sb.table("counseling_sessions").insert(payload).execute()
                    # Update applicant status to Counseled if currently earlier
                    sb.table("applicants").update({"status": "Counseled"})\
                        .eq("id", applicant["id"])\
                        .in_("status", ["New Lead","Contacted","Interested",
                                        "Documents Pending","Documents Submitted"])\
                        .execute()
                    st.success(f"✅ Session logged for {applicant['full_name']}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save: {e}")

    # ── Session history ───────────────────────────────────────
    with tab_history:
        filter_applicant = st.selectbox("Filter by applicant",
                                         ["All"] + list(applicants.keys()),
                                         key="hist_filter")
        aid = applicants[filter_applicant]["id"] if filter_applicant != "All" else None
        sessions = load_sessions(sb, aid)

        if not sessions:
            st.info("No sessions recorded yet.")
        else:
            for s in sessions:
                appl_info = s.get("applicants") or {}
                name = appl_info.get("full_name","—") if isinstance(appl_info, dict) else "—"
                reg  = appl_info.get("reg_number","") if isinstance(appl_info, dict) else ""
                with st.container():
                    hc1, hc2, hc3, hc4 = st.columns([2,2,2,1])
                    hc1.markdown(f"**{name}** `{reg}`")
                    hc2.markdown(f"📅 {s.get('session_date','—')}")
                    hc3.markdown(f"🏷️ {s.get('session_type','—')} — **{s.get('outcome','—')}**")
                    hc4.markdown(f"⏱️ {s.get('duration_mins','—')}m")
                    if s.get("next_action"):
                        st.caption(f"↪️ Next: {s['next_action']}")
                    st.divider()

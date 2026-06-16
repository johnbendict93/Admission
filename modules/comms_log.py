"""Module 19 — Communication Log"""
import streamlit as st
import pandas as pd
from datetime import date
from db import get_supabase
from config import MAROON, GOLD, CREAM

COMM_TYPES   = ["Call","SMS","WhatsApp","Email","Walk-in","Video Call","Other"]
COMM_OUTCOME = ["Answered","Not Answered","Interested","Not Interested",
                "Callback Requested","Left Message","Enrolled","Other"]


def load_applicants(sb):
    try:
        rows = sb.table("applicants").select("id, reg_number, full_name")\
            .order("full_name").execute().data or []
        return {f"{r['reg_number']} — {r['full_name']}": r["id"] for r in rows}
    except:
        return {}


def load_log(sb, applicant_id=None, comm_type=None, limit=50):
    try:
        q = sb.table("counseling_sessions").select(
            "id, session_date, session_type, outcome, next_action, "
            "duration_mins, notes, created_at, "
            "applicants(reg_number, full_name, mobile)"
        ).order("created_at", desc=True).limit(limit)
        if applicant_id:
            q = q.eq("applicant_id", applicant_id)
        if comm_type:
            q = q.eq("session_type", comm_type)
        return q.execute().data or []
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🗒️ Communication Log</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Complete history of all interactions with applicants.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_log, tab_add = st.tabs(["📋 View Log", "➕ Add Entry"])
    applicants = load_applicants(sb)

    with tab_log:
        fc1, fc2, fc3 = st.columns(3)
        filter_appl = fc1.selectbox("Applicant", ["All"] + list(applicants.keys()), key="cl_appl")
        filter_type = fc2.selectbox("Type", ["All"] + COMM_TYPES, key="cl_type")
        limit       = fc3.number_input("Show last", min_value=10, max_value=500,
                                        value=50, step=10)

        aid = applicants[filter_appl] if filter_appl != "All" else None
        ctype = filter_type if filter_type != "All" else None
        log = load_log(sb, aid, ctype, int(limit))

        st.markdown(f"**{len(log)} interaction(s)**")

        if not log:
            st.info("No communication records found.")
        else:
            for entry in log:
                appl  = entry.get("applicants") or {}
                name  = appl.get("full_name","—")  if isinstance(appl,dict) else "—"
                reg   = appl.get("reg_number","")  if isinstance(appl,dict) else ""
                mob   = appl.get("mobile","")      if isinstance(appl,dict) else ""
                dt    = (entry.get("session_date") or entry.get("created_at",""))[:10]
                stype = entry.get("session_type","—")
                out   = entry.get("outcome","—")
                nxt   = entry.get("next_action","")
                dur   = entry.get("duration_mins")
                notes = entry.get("notes","")

                with st.container():
                    c1, c2, c3 = st.columns([3, 2, 2])
                    c1.markdown(f"**{name}** `{reg}` · {mob}")
                    c2.markdown(f"📅 `{dt}` · **{stype}**")
                    c3.markdown(f"🏷️ {out}" + (f" · ⏱️{dur}m" if dur else ""))
                    if nxt:   st.caption(f"↪️ Next: {nxt}")
                    if notes: st.caption(f"📝 {notes}")
                    st.divider()

    with tab_add:
        st.subheader("Add Communication Entry")
        with st.form("comm_form", clear_on_submit=True):
            chosen = st.selectbox("Applicant *", ["—"] + list(applicants.keys()))
            cc1, cc2, cc3 = st.columns(3)
            comm_date = cc1.date_input("Date *", value=date.today())
            comm_type = cc2.selectbox("Type *", COMM_TYPES)
            duration  = cc3.number_input("Duration (mins)", min_value=1, max_value=180,
                                          value=10, step=5)
            outcome = st.selectbox("Outcome *", COMM_OUTCOME)
            next_action = st.text_input("Next Action",
                                         placeholder="e.g. Send brochure, call after 3 days")
            notes = st.text_area("Notes", height=80)

            if st.form_submit_button("💾 Save Entry", type="primary",
                                      use_container_width=True):
                if chosen == "—":
                    st.error("Select an applicant.")
                else:
                    payload = {
                        "applicant_id":  applicants[chosen],
                        "session_date":  comm_date.isoformat(),
                        "session_type":  comm_type,
                        "outcome":       outcome,
                        "next_action":   next_action.strip() or None,
                        "duration_mins": int(duration),
                        "notes":         notes.strip() or None,
                    }
                    try:
                        sb.table("counseling_sessions").insert(payload).execute()
                        st.success("✅ Communication logged!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")

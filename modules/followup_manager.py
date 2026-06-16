"""Module 11 — Follow-up Manager"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from db import get_supabase
from config import MAROON, GOLD, CREAM

PRIORITIES = ["Urgent", "High", "Normal", "Low"]
FU_STATUS  = ["Pending", "In Progress", "Done", "Cancelled"]
PRIORITY_ICON = {"Urgent":"🔴","High":"🟠","Normal":"🟡","Low":"🟢"}


def load_applicants(sb):
    try:
        rows = sb.table("applicants").select("id, reg_number, full_name")\
            .not_.in_("status",["Dropped","Not Interested"])\
            .order("full_name").execute().data or []
        return {f"{r['reg_number']} — {r['full_name']}": r["id"] for r in rows}
    except:
        return {}


def load_followups(sb, status_filter=None, priority_filter=None, overdue_only=False):
    try:
        q = sb.table("follow_ups").select(
            "id, title, due_date, priority, status, notes, applicant_id, "
            "applicants(reg_number, full_name, mobile)"
        ).order("due_date")
        if status_filter:
            q = q.in_("status", status_filter)
        if priority_filter:
            q = q.in_("priority", priority_filter)
        if overdue_only:
            q = q.lt("due_date", date.today().isoformat() + "T23:59:59")\
                  .eq("status", "Pending")
        return q.execute().data or []
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🔔 Follow-up Manager</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Create and track follow-up tasks for every applicant.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_add, tab_list = st.tabs(["➕ Add Follow-up", "📋 All Follow-ups"])
    applicants = load_applicants(sb)

    # ── Add follow-up ─────────────────────────────────────────
    with tab_add:
        with st.form("fu_form", clear_on_submit=True):
            chosen = st.selectbox("Applicant *", ["—"] + list(applicants.keys()))
            title  = st.text_input("Follow-up Title *",
                                    placeholder="e.g. Call to confirm admission")
            fc1, fc2, fc3 = st.columns(3)
            due_date = fc1.date_input("Due Date *",
                                       value=date.today() + timedelta(days=1))
            priority = fc2.selectbox("Priority", PRIORITIES)
            fu_type  = fc3.selectbox("Type", ["Call","WhatsApp","Email",
                                               "Visit","SMS","Other"])
            notes = st.text_area("Notes", height=68,
                                  placeholder="What needs to be done / discussed")
            if st.form_submit_button("💾 Save Follow-up",
                                      type="primary", use_container_width=True):
                if chosen == "—" or not title.strip():
                    st.error("Applicant and Title are required.")
                else:
                    payload = {
                        "applicant_id": applicants[chosen],
                        "title":        title.strip(),
                        "due_date":     due_date.isoformat(),
                        "priority":     priority,
                        "follow_up_type": fu_type,
                        "notes":        notes.strip() or None,
                        "status":       "Pending",
                    }
                    try:
                        sb.table("follow_ups").insert(payload).execute()
                        st.success("✅ Follow-up saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Save failed: {e}")

    # ── List ──────────────────────────────────────────────────
    with tab_list:
        lc1, lc2, lc3 = st.columns(3)
        f_status   = lc1.multiselect("Status",   FU_STATUS,  default=["Pending","In Progress"])
        f_priority = lc2.multiselect("Priority", PRIORITIES)
        overdue    = lc3.checkbox("Overdue only")

        fus = load_followups(sb, f_status or None, f_priority or None, overdue)
        st.markdown(f"**{len(fus)} follow-up(s)**")

        for fu in fus:
            appl = fu.get("applicants") or {}
            name   = appl.get("full_name","—") if isinstance(appl,dict) else "—"
            mobile = appl.get("mobile","")    if isinstance(appl,dict) else ""
            reg    = appl.get("reg_number","") if isinstance(appl,dict) else ""
            due    = (fu.get("due_date") or "")[:10]
            overdue_flag = due < date.today().isoformat() and fu["status"] == "Pending"

            with st.container():
                tc1, tc2, tc3, tc4 = st.columns([3,2,2,1])
                icon = PRIORITY_ICON.get(fu["priority"],"⚪")
                tc1.markdown(f"{icon} **{fu['title']}**  \n"
                             f"<small>{name} `{reg}` · {mobile}</small>",
                             unsafe_allow_html=True)
                tc2.markdown(f"📅 {'🔴 **OVERDUE** ' if overdue_flag else ''}{due}")
                tc3.markdown(f"`{fu['status']}`")
                # Inline status update
                new_s = tc4.selectbox("", FU_STATUS,
                                       index=FU_STATUS.index(fu["status"]),
                                       key=f"fu_{fu['id']}",
                                       label_visibility="collapsed")
                if new_s != fu["status"]:
                    try:
                        sb.table("follow_ups").update({"status": new_s})\
                            .eq("id", fu["id"]).execute()
                        st.rerun()
                    except:
                        pass
                if fu.get("notes"):
                    st.caption(fu["notes"])
                st.divider()

"""Module 12 — My Tasks (personal task board for logged-in counselor)"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from db import get_lookup, get_supabase
from config import MAROON, GOLD, CREAM

PRIORITY_ICON = {"Urgent":"🔴","High":"🟠","Normal":"🟡","Low":"🟢"}


def load_tasks(sb, show_done=False):
    try:
        q = sb.table("follow_ups").select(
            "id, title, due_date, priority, status, notes, applicant_id, "
            "applicants(reg_number, full_name)"
        ).order("due_date")
        if not show_done:
            q = q.in_("status", ["Pending", "In Progress"])
        return q.execute().data or []
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>✅ My Tasks</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Your personal task view — all pending follow-ups assigned to you.
        </p>
    </div>""", unsafe_allow_html=True)

    show_done = st.toggle("Show completed tasks", value=False)
    tasks = load_tasks(sb, show_done)

    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    overdue   = [t for t in tasks if (t.get("due_date","9")[:10] < today) and t["status"] == "Pending"]
    due_today = [t for t in tasks if t.get("due_date","")[:10] == today]
    upcoming  = [t for t in tasks if t.get("due_date","")[:10] > today]
    done      = [t for t in tasks if t["status"] in ["Done","Cancelled"]] if show_done else []

    # ── KPI strip ─────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    for col, icon, val, label, color in [
        (k1, "🔴", len(overdue),   "Overdue",    "#E74C3C"),
        (k2, "🟡", len(due_today), "Due Today",  "#F39C12"),
        (k3, "📅", len(upcoming),  "Upcoming",   "#3498DB"),
        (k4, "✅", len(done),      "Completed",  "#27AE60"),
    ]:
        with col:
            st.markdown(
                f"<div style='background:{color}22;border:1px solid {color};"
                f"border-radius:8px;padding:10px;text-align:center;'>"
                f"<h3 style='margin:0;color:{color};'>{icon} {val}</h3>"
                f"<small>{label}</small></div>",
                unsafe_allow_html=True
            )

    st.divider()

    def render_task_group(title, task_list, color):
        if not task_list:
            return
        st.markdown(f"### {title}")
        for t in task_list:
            appl = t.get("applicants") or {}
            name = appl.get("full_name","—") if isinstance(appl,dict) else "—"
            reg  = appl.get("reg_number","") if isinstance(appl,dict) else ""
            due  = (t.get("due_date") or "")[:10]
            icon = PRIORITY_ICON.get(t.get("priority",""),"⚪")

            with st.container():
                c1, c2, c3 = st.columns([4, 2, 1])
                c1.markdown(
                    f"{icon} **{t['title']}**  \n"
                    f"<small style='color:#666;'>{name} · {reg}</small>",
                    unsafe_allow_html=True
                )
                c2.markdown(f"📅 `{due}`  \n`{t['status']}`")
                new_status = c3.selectbox(
                    "", ["Pending","In Progress","Done","Cancelled"],
                    index=["Pending","In Progress","Done","Cancelled"].index(t["status"])
                    if t["status"] in ["Pending","In Progress","Done","Cancelled"] else 0,
                    key=f"task_{t['id']}",
                    label_visibility="collapsed"
                )
                if new_status != t["status"]:
                    try:
                        sb.table("follow_ups").update({"status": new_status})\
                            .eq("id", t["id"]).execute()
                        st.rerun()
                    except:
                        pass
                if t.get("notes"):
                    st.caption(t["notes"])
                st.divider()

    render_task_group("🔴 Overdue",   overdue,   "#E74C3C")
    render_task_group("🟡 Due Today", due_today, "#F39C12")
    render_task_group("📅 Upcoming",  upcoming,  "#3498DB")
    if show_done:
        render_task_group("✅ Completed", done, "#27AE60")

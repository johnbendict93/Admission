"""Module 21 — Calendar & Events"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from db import get_supabase
from config import MAROON, GOLD, CREAM

EVENT_TYPES = ["Open Day","Counseling Camp","Deadline","Exam","Orientation",
               "Fee Due","Meeting","Holiday","Other"]

# Static DCE academic calendar 2026-27 seed events
SEED_EVENTS = [
    {"date": "2026-07-01", "title": "Commencement of Classes 2026-27",     "type": "Orientation"},
    {"date": "2026-07-15", "title": "Last Date for Fee Payment (1st Inst)","type": "Fee Due"},
    {"date": "2026-08-15", "title": "Independence Day — Holiday",           "type": "Holiday"},
    {"date": "2026-09-05", "title": "Teachers Day Celebration",             "type": "Other"},
    {"date": "2026-10-02", "title": "Gandhi Jayanti — Holiday",             "type": "Holiday"},
    {"date": "2026-11-01", "title": "Internal Assessment I",                "type": "Exam"},
    {"date": "2026-11-14", "title": "Children's Day Event",                 "type": "Other"},
    {"date": "2026-12-25", "title": "Christmas — Holiday",                  "type": "Holiday"},
    {"date": "2027-01-15", "title": "Pongal Holidays Begin",                "type": "Holiday"},
    {"date": "2027-01-26", "title": "Republic Day — Holiday",               "type": "Holiday"},
    {"date": "2027-02-01", "title": "Internal Assessment II",               "type": "Exam"},
    {"date": "2027-03-15", "title": "End Semester Exam Begin",              "type": "Exam"},
    {"date": "2027-04-01", "title": "Last Date for Fee Payment (2nd Inst)", "type": "Fee Due"},
]


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>📅 Calendar & Events</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            DCE academic calendar and admission events for 2026-27.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_upcoming, tab_add = st.tabs(["📅 Upcoming Events", "➕ Add Event"])

    with tab_upcoming:
        # Merge seed events with any stored follow-up events
        events = list(SEED_EVENTS)
        try:
            fu_rows = sb.table("follow_ups").select(
                "title, due_date, follow_up_type"
            ).gte("due_date", date.today().isoformat()).order("due_date").execute().data or []
            for f in fu_rows:
                events.append({
                    "date":  (f.get("due_date") or "")[:10],
                    "title": f.get("title",""),
                    "type":  "Follow-up",
                })
        except:
            pass

        events.sort(key=lambda x: x["date"])

        # Filter controls
        fc1, fc2 = st.columns(2)
        f_type = fc1.multiselect("Filter by Type", EVENT_TYPES + ["Follow-up"])
        today_str = date.today().isoformat()
        show_past = fc2.checkbox("Include past events", value=False)

        TYPE_COLOR = {
            "Open Day": MAROON, "Counseling Camp": MAROON, "Fee Due": "#E74C3C",
            "Exam": "#9B59B6", "Deadline": "#E67E22", "Orientation": "#27AE60",
            "Meeting": "#3498DB", "Holiday": "#16A085", "Follow-up": GOLD, "Other": "#888",
        }

        for ev in events:
            if not show_past and ev["date"] < today_str:
                continue
            if f_type and ev["type"] not in f_type:
                continue
            color = TYPE_COLOR.get(ev["type"], "#888")
            days_away = (date.fromisoformat(ev["date"]) - date.today()).days
            badge = ""
            if days_away == 0:   badge = "🔴 **TODAY**"
            elif days_away == 1: badge = "🟠 Tomorrow"
            elif days_away < 7:  badge = f"🟡 In {days_away} days"
            elif days_away < 0:  badge = f"<small style='color:#aaa;'>Past</small>"

            st.markdown(
                f"<div style='border-left:4px solid {color};padding:8px 14px;"
                f"margin:6px 0;background:{color}11;border-radius:0 6px 6px 0;'>"
                f"<b style='color:{color};'>{ev['date']}</b> &nbsp; {ev['title']} "
                f"&nbsp; <span style='background:{color};color:#fff;padding:1px 8px;"
                f"border-radius:10px;font-size:0.75rem;'>{ev['type']}</span> {badge}"
                f"</div>",
                unsafe_allow_html=True
            )

    with tab_add:
        st.subheader("Add New Event / Reminder")
        with st.form("event_form", clear_on_submit=True):
            title     = st.text_input("Event Title *", placeholder="e.g. Walk-in Camp at Velachery")
            ec1, ec2  = st.columns(2)
            event_date = ec1.date_input("Date *", value=date.today() + timedelta(days=7))
            event_type = ec2.selectbox("Type", EVENT_TYPES)
            notes      = st.text_area("Notes", height=68)

            if st.form_submit_button("💾 Add Event", type="primary",
                                      use_container_width=True):
                if not title.strip():
                    st.error("Title is required.")
                else:
                    # Store as a follow-up with no applicant_id for now
                    try:
                        sb.table("follow_ups").insert({
                            "title":           title.strip(),
                            "due_date":        event_date.isoformat(),
                            "follow_up_type":  event_type,
                            "notes":           notes.strip() or None,
                            "priority":        "Normal",
                            "status":          "Pending",
                        }).execute()
                        st.success(f"✅ Event '{title}' added on {event_date}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")

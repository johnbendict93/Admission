"""Module 11 — Follow-up Manager"""
import streamlit as st


def show():
    tab1, tab2, tab3 = st.tabs(["⏰ Overdue", "📅 Today", "📆 Upcoming"])
    for tab, label in zip([tab1, tab2, tab3], ["Overdue", "Today", "Upcoming"]):
        with tab:
            st.markdown(f"""
            <div class="module-placeholder">
                <h3>🔔 {label} Follow-ups</h3>
                <p>List from <code>follow_ups</code> table filtered by due_date<br>
                Mark complete, reschedule, or add note inline</p>
            </div>
            """, unsafe_allow_html=True)

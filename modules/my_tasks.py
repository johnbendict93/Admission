"""Module 12 — My Tasks"""
import streamlit as st


def show():
    st.subheader("✅ My Tasks & Reminders")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("""
        <div class="module-placeholder">
            <p>Follow-ups assigned to the logged-in user<br>
            Grouped: Overdue | Today | This Week<br>
            Click to expand → mark complete, add note</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.subheader("➕ Quick Task")
        with st.form("quick_task"):
            title    = st.text_input("Task")
            due      = st.date_input("Due")
            priority = st.selectbox("Priority", ["Urgent", "High", "Normal", "Low"])
            st.form_submit_button("Add", use_container_width=True)

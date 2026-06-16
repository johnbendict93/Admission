"""Module 21 — Calendar & Events"""
import streamlit as st


def show():
    st.subheader("📅 Admission Calendar")
    st.markdown("""
    <div class="module-placeholder">
        <h3>Event Calendar</h3>
        <p>Key dates: Application Deadline, Document Submission, Counseling Days,<br>
        Fee Payment Deadline, Orientation, Semester Start<br>
        Add custom events, set reminders, sync with Google Calendar (planned)</p>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("➕ Add Event")
    with st.form("event_form"):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Event Title")
        date  = c2.date_input("Date")
        etype = c3.selectbox("Type", ["Deadline", "Counseling", "Orientation", "Exam", "Holiday", "Other"])
        desc  = st.text_area("Description")
        st.form_submit_button("Add to Calendar", use_container_width=True)

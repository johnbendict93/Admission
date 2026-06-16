"""Module 10 — Counseling Sessions"""
import streamlit as st


SESSION_TYPES = ["Walk-in", "Phone Call", "Video Call", "WhatsApp", "Email", "Home Visit", "School Visit", "Camp", "Follow-up"]
OUTCOMES = ["Interested", "Not Interested", "Need More Time", "Documents Requested",
            "Fee Discussed", "Confirmed", "Dropped", "Callback Scheduled", "Other"]


def show():
    tab1, tab2 = st.tabs(["📋 Session History", "➕ Log New Session"])
    with tab1:
        st.markdown("""
        <div class="module-placeholder">
            <h3>All Counseling Sessions</h3>
            <p>Table from <code>counseling_sessions</code> joined with applicants + users<br>
            Filter by counselor, date, outcome, session type</p>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        with st.form("session_form"):
            applicant = st.text_input("Applicant Reg# or Name *")
            c1, c2 = st.columns(2)
            s_type   = c1.selectbox("Session Type *", SESSION_TYPES)
            s_date   = c2.date_input("Session Date *")
            duration = st.number_input("Duration (mins)", 5, 240, 30)
            outcome  = st.selectbox("Outcome *", OUTCOMES)
            next_action = st.text_input("Next Action")
            next_date   = st.date_input("Next Action Date")
            notes       = st.text_area("Session Notes")
            st.form_submit_button("💾 Save Session", use_container_width=True)

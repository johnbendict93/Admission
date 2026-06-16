"""Module 13 — Application Tracker"""
import streamlit as st


STAGES = [
    "Draft", "Submitted", "Under Review", "Documents Verified",
    "Merit Listed", "Seat Allotted", "Fee Pending",
    "Provisionally Admitted", "Admitted", "Rejected", "Withdrawn"
]


def show():
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("""
        <div class="module-placeholder">
            <h3>📝 All Applications</h3>
            <p>Table from <code>applications</code> joined with applicants<br>
            Columns: App#, Name, Dept, Programme, Stage, Seat Type, Reviewed By<br>
            Click to open → change stage, add remark</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.subheader("Stage Filter")
        for stage in STAGES:
            st.checkbox(stage, key=f"stage_{stage}")

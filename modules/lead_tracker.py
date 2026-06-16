"""Module 04 — Lead Tracker"""
import streamlit as st
from config import APPLICANT_STATUSES, DEPARTMENTS


def show():
    # Filters
    with st.expander("🔍 Filters", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        status_filter = c1.multiselect("Status", APPLICANT_STATUSES)
        dept_filter   = c2.multiselect("Department", DEPARTMENTS)
        source_filter = c3.text_input("Lead Source")
        search        = c4.text_input("Search name / phone / reg#")

    st.markdown("""
    <div class="module-placeholder">
        <h3>📋 Leads Table</h3>
        <p>Query <code>applicants</code> table with filters above.<br>
        Columns: Reg#, Name, Phone, Status, Dept, Counselor, Last Activity<br>
        Click a row to open applicant profile.</p>
    </div>
    """, unsafe_allow_html=True)

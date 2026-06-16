"""Module 07 — Applicant Profiles"""
import streamlit as st


def show():
    st.info("Search or select an applicant to view their full profile.")
    search = st.text_input("🔍 Search by name, phone, or registration number")
    st.markdown("""
    <div class="module-placeholder">
        <h3>👤 Applicant Profile Card</h3>
        <p>Tabs: Personal | Academic | Applications | Counseling History | Documents | Follow-ups<br>
        Edit-in-place fields, status badge, priority flag<br>
        All data from <code>applicants</code> + joined tables</p>
    </div>
    """, unsafe_allow_html=True)

"""Module 16 — Scholarship Management"""
import streamlit as st


def show():
    tab1, tab2 = st.tabs(["🎓 Scholarship Applicants", "📋 Scheme Master"])
    with tab1:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Scholarship Applicants</h3>
            <p>List of applicants eligible / applied for govt/management scholarships<br>
            Status: Applied | Documents Submitted | Approved | Disbursed</p>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Scholarship Schemes</h3>
            <p>BC/MBC/SC/ST Scholarship, First Graduate, Sports, NRI concession etc.<br>
            Eligibility criteria, amount, applying authority</p>
        </div>
        """, unsafe_allow_html=True)

"""Module 19 — Communication Log"""
import streamlit as st


def show():
    st.markdown("""
    <div class="module-placeholder">
        <h3>🗒️ Communication Log</h3>
        <p>Unified timeline of all touchpoints per applicant or across all applicants<br>
        Source: counseling_sessions + follow_ups + SMS/email blast logs<br>
        Filter by channel, date, counselor, applicant</p>
    </div>
    """, unsafe_allow_html=True)

"""Module 20 — Hostel Allotment"""
import streamlit as st


def show():
    tab1, tab2 = st.tabs(["🏠 Room Allotment", "📋 Hostel Applicants"])
    with tab1:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Hostel Room Matrix</h3>
            <p>Block → Floor → Room → Bed mapping<br>
            Occupied / Available / Reserved status<br>
            Allot applicant to a bed, generate allotment letter</p>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        st.markdown("""
        <div class="module-placeholder">
            <p>Applicants who opted for hostel (preferred_hostel = TRUE)<br>
            Gender-wise filter, waitlist management</p>
        </div>
        """, unsafe_allow_html=True)

"""Module 02 — Analytics & Reports"""
import streamlit as st


def show():
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Conversion Report", "📅 Daily Activity", "👤 Counselor Performance", "📤 Export"
    ])
    with tab1:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Conversion Funnel Report</h3>
            <p>Lead → Contacted → Interested → Enrolled conversion rates<br>
            Filter by date range, department, counselor, lead source</p>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Daily Activity Log</h3>
            <p>Sessions created, follow-ups completed, new registrations per day</p>
        </div>
        """, unsafe_allow_html=True)
    with tab3:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Counselor Leaderboard</h3>
            <p>Leads handled, conversion rate, avg sessions per lead per counselor</p>
        </div>
        """, unsafe_allow_html=True)
    with tab4:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Export Reports</h3>
            <p>Download Excel / CSV / PDF reports for any date range</p>
        </div>
        """, unsafe_allow_html=True)

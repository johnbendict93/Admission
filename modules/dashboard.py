"""Module 01 — Dashboard"""
import streamlit as st
from config import MAROON, GOLD


def show():
    # KPI row
    col1, col2, col3, col4 = st.columns(4)
    kpis = [
        ("Total Applicants", "—", "👤"),
        ("Enrolled Today",   "—", "✅"),
        ("Pending Follow-ups","—", "🔔"),
        ("Open Seats",       "—", "🪑"),
    ]
    for col, (label, val, icon) in zip([col1, col2, col3, col4], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{icon} {val}</h3>
                <p>{label}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("📈 Application Pipeline")
        st.markdown("""
        <div class="module-placeholder">
            <h3>Pipeline Chart</h3>
            <p>Funnel: New Lead → Contacted → Counseled → Enrolled</p>
            <p><em>Wire up Supabase query + Plotly funnel chart here</em></p>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.subheader("📋 Today's Follow-ups")
        st.markdown("""
        <div class="module-placeholder">
            <p>List of today's pending follow-ups<br>from <code>follow_ups</code> table</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🏫 Department-wise Enrolment")
        st.markdown("""
        <div class="module-placeholder">
            <p>Bar chart: seats filled vs. intake per dept</p>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.subheader("📡 Lead Source Breakdown")
        st.markdown("""
        <div class="module-placeholder">
            <p>Pie chart: Walk-in / Phone / Social Media etc.</p>
        </div>
        """, unsafe_allow_html=True)

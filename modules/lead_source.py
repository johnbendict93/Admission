"""Module 05 — Lead Source Analysis"""
import streamlit as st


def show():
    st.markdown("""
    <div class="module-placeholder">
        <h3>📡 Lead Source Analysis</h3>
        <p>Charts: leads by source (Walk-in, Phone, Social, Reference…)<br>
        Conversion rate per source, cost-per-lead if campaign data is entered,<br>
        trend over weeks/months.</p>
    </div>
    """, unsafe_allow_html=True)

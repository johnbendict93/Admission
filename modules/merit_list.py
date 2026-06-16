"""Module 09 — Merit List"""
import streamlit as st
from config import DEPARTMENTS


def show():
    c1, c2, c3 = st.columns(3)
    dept  = c1.selectbox("Department", DEPARTMENTS)
    prog  = c2.selectbox("Programme", ["B.E.", "B.Tech"])
    cat   = c3.selectbox("Category", ["All", "OC", "BC", "MBC", "SC", "ST"])
    st.markdown("""
    <div class="module-placeholder">
        <h3>🏅 Merit List</h3>
        <p>Ranked table of applicants by cutoff marks for selected dept/programme/category<br>
        Highlight seat-allotted vs pending<br>
        Export to PDF/Excel</p>
    </div>
    """, unsafe_allow_html=True)

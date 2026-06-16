"""Module 14 — Seat Allotment"""
import streamlit as st
from config import DEPARTMENTS


def show():
    st.subheader("🪑 Seat Allotment Dashboard")
    dept = st.selectbox("Select Department", DEPARTMENTS)
    st.markdown("""
    <div class="module-placeholder">
        <h3>Seat Matrix</h3>
        <p>Intake | Management Quota | Government Quota | NRI | Lateral Entry<br>
        Filled vs available counts, with applicant list per cell<br>
        Allot button → updates <code>applications.allotted_seat_type</code></p>
    </div>
    """, unsafe_allow_html=True)

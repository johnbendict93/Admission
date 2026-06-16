"""Module 03 — Walk-in Registration"""
import streamlit as st
from config import DEPARTMENTS, CATEGORIES, LEAD_SOURCES, MAROON, GOLD


def show():
    st.info("Register a new walk-in applicant. All fields marked * are required.")
    with st.form("walkin_form"):
        st.subheader("👤 Personal Details")
        c1, c2, c3 = st.columns(3)
        first_name  = c1.text_input("First Name *")
        last_name   = c2.text_input("Last Name *")
        dob         = c3.date_input("Date of Birth")

        c4, c5, c6 = st.columns(3)
        gender      = c4.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        phone       = c5.text_input("Mobile *")
        email       = c6.text_input("Email")

        st.subheader("🏫 Academic Details")
        c7, c8, c9 = st.columns(3)
        twelfth_pct = c7.number_input("12th %", 0.0, 100.0, step=0.01)
        cutoff      = c8.number_input("Cutoff Marks", 0.0, 200.0, step=0.01)
        category    = c9.selectbox("Category", CATEGORIES)

        c10, c11 = st.columns(2)
        programme   = c10.selectbox("Programme", ["B.E.", "B.Tech", "M.E.", "M.Tech", "MBA", "MCA"])
        department  = c11.selectbox("Preferred Department", DEPARTMENTS)

        st.subheader("📡 Lead Info")
        c12, c13 = st.columns(2)
        source      = c12.selectbox("Lead Source", LEAD_SOURCES)
        referred_by = c13.text_input("Referred By")
        notes       = st.text_area("Notes")

        submitted = st.form_submit_button("💾 Register Applicant", use_container_width=True)
        if submitted:
            st.success("✅ Applicant registered! (Supabase INSERT not yet wired)")

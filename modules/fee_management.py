"""Module 15 — Fee Management"""
import streamlit as st


def show():
    tab1, tab2, tab3 = st.tabs(["💳 Collect Fee", "📋 Fee Records", "📊 Collection Report"])
    with tab1:
        with st.form("fee_form"):
            reg = st.text_input("Applicant Reg# *")
            c1, c2 = st.columns(2)
            fee_type = c1.selectbox("Fee Type", ["Application Fee", "Admission Fee", "Tuition Fee", "Hostel Fee", "Transport Fee"])
            amount   = c2.number_input("Amount (₹)", min_value=0)
            c3, c4   = st.columns(2)
            mode     = c3.selectbox("Payment Mode", ["Cash", "DD", "Online", "NEFT", "Cheque"])
            ref_no   = c4.text_input("Reference / Receipt No.")
            st.form_submit_button("💾 Record Payment", use_container_width=True)
    with tab2:
        st.markdown("""<div class="module-placeholder"><p>Fee records table with receipt download</p></div>""", unsafe_allow_html=True)
    with tab3:
        st.markdown("""<div class="module-placeholder"><p>Collection summary by dept / fee type / date range</p></div>""", unsafe_allow_html=True)

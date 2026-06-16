"""Module 18 — Email Campaigns"""
import streamlit as st


def show():
    tab1, tab2 = st.tabs(["✉️ Compose Campaign", "📬 Campaign History"])
    with tab1:
        subject  = st.text_input("Subject Line")
        audience = st.multiselect("To (segment)", ["All Leads", "Confirmed", "Fee Pending", "Interested"])
        body     = st.text_area("Email Body (HTML supported)", height=200)
        c1, c2   = st.columns(2)
        schedule = c1.checkbox("Schedule for later")
        if schedule:
            send_at = c2.date_input("Send Date")
        if st.button("📤 Send / Schedule", use_container_width=True):
            st.info("Email integration (SMTP / SendGrid) not yet wired.")
    with tab2:
        st.markdown("""<div class="module-placeholder"><p>Past campaigns: subject, sent count, open rate, click rate</p></div>""", unsafe_allow_html=True)

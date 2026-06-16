"""Module 17 — SMS / WhatsApp Blast"""
import streamlit as st
from config import APPLICANT_STATUSES


def show():
    st.info("Compose and send bulk SMS or WhatsApp messages to filtered applicants.")
    c1, c2 = st.columns(2)
    channel   = c1.radio("Channel", ["SMS", "WhatsApp"], horizontal=True)
    audience  = c2.multiselect("Target Audience (by status)", APPLICANT_STATUSES)
    template  = st.selectbox("Message Template", ["Custom", "Fee Reminder", "Document Request", "Admission Confirmation", "Event Invite"])
    message   = st.text_area("Message Body", max_chars=160 if channel == "SMS" else 1024,
                             help="Use {name}, {reg_no} as merge tags")
    st.caption(f"{len(message)} characters")
    c3, c4 = st.columns(2)
    c3.metric("Estimated Recipients", "—")
    if c4.button("🚀 Send Now", use_container_width=True):
        st.warning("Confirm send? (SMS gateway integration pending)")

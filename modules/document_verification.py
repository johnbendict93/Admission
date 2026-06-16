"""Module 08 — Document Verification"""
import streamlit as st


DOCUMENTS = [
    "12th Mark Sheet", "10th Mark Sheet", "Transfer Certificate",
    "Community Certificate", "Income Certificate", "Aadhar Card",
    "Passport Photo", "Entrance Score Card", "Conduct Certificate",
]


def show():
    st.info("Select an applicant and verify / upload their documents.")
    applicant = st.text_input("🔍 Applicant Reg# or Name")
    if applicant:
        st.subheader("Document Checklist")
        for doc in DOCUMENTS:
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(doc)
            c2.selectbox("Status", ["Pending", "Received", "Verified", "Rejected"],
                         key=f"doc_status_{doc}", label_visibility="collapsed")
            c3.button("📎 Upload", key=f"doc_upload_{doc}")
        st.button("💾 Save Verification Status", use_container_width=True)

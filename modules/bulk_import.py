"""Module 06 — Bulk Import Leads"""
import streamlit as st


def show():
    st.subheader("📥 Bulk Import Leads from Excel / CSV")
    st.markdown("Download the template, fill it in, and upload to batch-insert applicants.")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇️ Download Template", data="First Name,Last Name,Phone,Email,Department\n",
                           file_name="dce_lead_import_template.csv", mime="text/csv")
    with col2:
        uploaded = st.file_uploader("Upload filled template", type=["csv", "xlsx"])
        if uploaded:
            st.info("Preview & validate rows here, then click Import.")
            st.markdown("""
            <div class="module-placeholder">
                <p>Parsed rows preview table<br>Duplicate phone detection<br>
                Supabase upsert on confirm</p>
            </div>
            """, unsafe_allow_html=True)

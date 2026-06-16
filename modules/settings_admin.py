"""Module 22 — Settings & Admin"""
import streamlit as st


def show():
    tab1, tab2, tab3, tab4 = st.tabs(["👥 User Management", "🏫 College Config", "🔗 Integrations", "🛡️ Roles & Permissions"])
    with tab1:
        st.markdown("""
        <div class="module-placeholder">
            <h3>CRM Users</h3>
            <p>Add / edit / deactivate staff accounts<br>
            Assign role: Admin | Counselor | Staff | Viewer<br>
            Data from <code>users</code> table (Supabase Auth linked)</p>
        </div>
        """, unsafe_allow_html=True)
    with tab2:
        with st.form("college_config"):
            st.text_input("College Name", value="Dhanalakshmi College of Engineering")
            st.text_input("Academic Year", value="2026-27")
            st.text_input("Principal Name")
            st.text_input("Admission Officer")
            st.form_submit_button("💾 Save", use_container_width=True)
    with tab3:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Integrations</h3>
            <p>Supabase URL & Key (read from secrets)<br>
            SMS Gateway (e.g. Textlocal / MSG91)<br>
            Email SMTP / SendGrid<br>
            WhatsApp Business API</p>
        </div>
        """, unsafe_allow_html=True)
    with tab4:
        st.markdown("""
        <div class="module-placeholder">
            <h3>Role Matrix</h3>
            <p>Admin: full access<br>
            Counselor: own applicants + sessions + follow-ups<br>
            Staff: all applicants, no user management<br>
            Viewer: read-only dashboards</p>
        </div>
        """, unsafe_allow_html=True)

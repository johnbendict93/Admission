"""Module 18 — Email Campaigns"""
import streamlit as st
import pandas as pd
from db import get_supabase
from config import MAROON, GOLD, CREAM, APPLICANT_STATUSES, DEPARTMENTS

EMAIL_TEMPLATES = {
    "Open Day Invite": {
        "subject": "You're Invited — DCE Open Day 2026",
        "body": """Dear {name},

We are pleased to invite you to the DCE Open Day on {date}.

Come explore our state-of-the-art campus, meet faculty, and learn about {programme} at Dhanalakshmi College of Engineering.

Date: {date}
Venue: DCE Campus, Tambaram, Chennai

Register now or call us at 044-XXXXXXXX.

Warm regards,
DCE Admissions Team"""
    },
    "Application Follow-up": {
        "subject": "Your DCE Application — Next Steps",
        "body": """Dear {name},

Thank you for your interest in DCE. Your enquiry for {programme} has been received.

Kindly complete your application by submitting the required documents at our admission office or online portal.

For queries, call: 044-XXXXXXXX

Best regards,
DCE Admissions"""
    },
    "Custom": {"subject": "", "body": ""},
}


def load_recipients(sb, status_filter, dept_filter):
    try:
        q = sb.table("applicants").select(
            "id, reg_number, full_name, email, mobile, "
            "programme_interested, status"
        ).not_.is_("email", "null").neq("email", "")
        if status_filter:
            q = q.in_("status", status_filter)
        if dept_filter:
            q = q.in_("department_interested", dept_filter)
        return q.execute().data or []
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>📧 Email Campaigns</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Send targeted email campaigns to applicant groups.
        </p>
    </div>""", unsafe_allow_html=True)

    st.subheader("Audience")
    fc1, fc2 = st.columns(2)
    f_status = fc1.multiselect("By Status",     APPLICANT_STATUSES)
    f_dept   = fc2.multiselect("By Department", DEPARTMENTS)

    recipients = load_recipients(sb, f_status or None, f_dept or None)
    st.markdown(f"**{len(recipients)} recipient(s) with email addresses**")

    if recipients:
        with st.expander("Preview recipients"):
            df = pd.DataFrame(recipients)[["full_name","email","mobile","status"]]
            df.columns = ["Name","Email","Mobile","Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Compose Email")

    template_name = st.selectbox("Template", list(EMAIL_TEMPLATES.keys()))
    tpl = EMAIL_TEMPLATES[template_name]

    subject = st.text_input("Subject *", value=tpl["subject"])
    body    = st.text_area("Email Body *", value=tpl["body"], height=250)

    if recipients:
        sample = recipients[0]
        with st.expander("📄 Preview (first recipient)"):
            preview = body\
                .replace("{name}", sample["full_name"])\
                .replace("{programme}", sample.get("programme_interested",""))\
                .replace("{date}", "30 Jun 2026")
            st.text(preview)

    st.divider()
    st.warning("⚠️ Connect an SMTP / SendGrid / AWS SES account in Settings to enable sending.")

    if st.button(f"📧 Send to {len(recipients)} Recipient(s)",
                 type="primary",
                 disabled=not recipients or not subject.strip() or not body.strip()):
        st.info("Email API not yet configured. Add SMTP settings in Settings & Admin.")

    if recipients:
        df_exp = pd.DataFrame(recipients)[["full_name","email","mobile","status"]]
        csv = df_exp.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export Email List (CSV)", csv, "email_list.csv","text/csv")

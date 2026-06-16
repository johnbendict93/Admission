"""Module 17 — SMS / WhatsApp Blast"""
import streamlit as st
import pandas as pd
from config import MAROON, GOLD, CREAM, DEPARTMENTS, PROGRAMMES, APPLICANT_STATUSES, LEAD_SOURCES

TEMPLATES = {
    "Walk-in Invitation": "Dear {name}, DCE Open Day is on {date}. Visit us at Tambaram and explore {programme}. Call: 044-XXXXXXXX",
    "Follow-up Reminder": "Dear {name}, Thank you for visiting DCE. Your application for {programme} is pending. Call us: 044-XXXXXXXX",
    "Seat Confirmation":  "Dear {name}, Congratulations! Your seat in {programme} – {dept} at DCE is confirmed. Complete formalities by {date}.",
    "Fee Reminder":       "Dear {name}, Your fee for {programme} is due. Pay before {date} to secure your seat. DCE Admissions.",
    "Document Reminder":  "Dear {name}, Kindly submit your pending documents at DCE admission office at the earliest. DCE Admissions.",
    "Custom":             "",
}


def load_filtered_applicants(sb, status_filter, dept_filter, source_filter):
    try:
        q = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, "
            "programme_interested, department_interested, status"
        )
        if status_filter:
            q = q.in_("status", status_filter)
        if dept_filter:
            q = q.in_("department_interested", dept_filter)
        if source_filter:
            q = q.in_("lead_source", source_filter)
        return q.execute().data or []
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def show():
    sb = get_supabase()
    DEPARTMENTS  = get_lookup('department')
    LEAD_SOURCES = get_lookup('lead_source')

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>💬 SMS / WhatsApp Blast</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Send bulk SMS or WhatsApp messages to filtered groups of applicants.
        </p>
    </div>""", unsafe_allow_html=True)

    # ── Step 1: Audience ──────────────────────────────────────
    st.subheader("Step 1 — Select Audience")
    fc1, fc2, fc3 = st.columns(3)
    f_status = fc1.multiselect("By Status",      APPLICANT_STATUSES)
    f_dept   = fc2.multiselect("By Department",  DEPARTMENTS)
    f_source = fc3.multiselect("By Lead Source", LEAD_SOURCES)

    recipients = load_filtered_applicants(sb, f_status or None,
                                          f_dept or None, f_source or None)
    st.markdown(f"**{len(recipients)} recipient(s) selected**")

    if recipients:
        with st.expander("Preview recipient list"):
            df = pd.DataFrame(recipients)[["reg_number","full_name","mobile","status"]]
            df.columns = ["Reg No","Name","Mobile","Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Step 2: Message ───────────────────────────────────────
    st.subheader("Step 2 — Compose Message")
    channel  = st.radio("Channel", ["SMS","WhatsApp"], horizontal=True)
    template = st.selectbox("Template", list(TEMPLATES.keys()))

    default_msg = TEMPLATES[template]
    message = st.text_area("Message *", value=default_msg, height=120,
                            max_chars=500,
                            placeholder="Use {name}, {programme}, {dept}, {date} as placeholders")
    char_count = len(message)
    sms_count  = (char_count // 160) + 1
    st.caption(f"{char_count}/500 chars · ~{sms_count} SMS credit(s) per recipient")

    st.divider()

    # ── Step 3: Send (preview mode) ───────────────────────────
    st.subheader("Step 3 — Review & Send")
    if recipients:
        sample = recipients[0]
        preview_msg = message\
            .replace("{name}", sample["full_name"])\
            .replace("{programme}", sample.get("programme_interested",""))\
            .replace("{dept}", sample.get("department_interested",""))\
            .replace("{date}", "30 Jun 2026")
        st.markdown("**Preview (first recipient):**")
        st.info(preview_msg)

    st.warning("⚠️ This module is ready for integration with an SMS/WhatsApp API "
               "(e.g. Twilio, MSG91, 2Factor). Connect your API key in Settings to enable actual sending.")

    col_send, col_export = st.columns(2)
    if col_send.button(f"🚀 Send {channel} to {len(recipients)} Recipient(s)",
                       type="primary", use_container_width=True,
                       disabled=not recipients or not message.strip()):
        st.info("📡 API integration needed — configure your SMS/WhatsApp provider in Settings & Admin.")

    if recipients and col_export.button("⬇️ Export Numbers (CSV)", use_container_width=True):
        df_exp = pd.DataFrame(recipients)[["full_name","mobile","status"]]
        csv = df_exp.to_csv(index=False).encode("utf-8")
        st.download_button("Download", csv, "recipients.csv", "text/csv")

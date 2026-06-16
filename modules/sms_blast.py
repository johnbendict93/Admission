"""Module 17 — SMS / WhatsApp Blast (100% dynamic — templates from Supabase)"""
import streamlit as st
import pandas as pd
from datetime import date
from config import MAROON, GOLD, APPLICANT_STATUSES
from db import get_supabase, get_lookup, get_settings_by_category


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
        st.error(f"Error loading recipients: {e}")
        return []


def load_sms_templates(sb) -> dict:
    """Load SMS templates dynamically from settings table."""
    try:
        rows = sb.table("settings").select("key, value") \
            .eq("category", "sms_template").eq("is_active", True) \
            .order("key").execute().data or []
        return {r["key"]: r["value"] for r in rows}
    except:
        return {"Custom": ""}


def show():
    sb = get_supabase()
    DEPARTMENTS  = get_lookup("department")
    LEAD_SOURCES = get_lookup("lead_source")
    templates    = load_sms_templates(sb)

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

    recipients = load_filtered_applicants(
        sb,
        f_status or None,
        f_dept   or None,
        f_source or None
    )
    st.markdown(f"**{len(recipients)} recipient(s) selected**")

    if recipients:
        with st.expander("Preview recipient list"):
            df = pd.DataFrame(recipients)[["reg_number", "full_name", "mobile", "status"]]
            df.columns = ["Reg No", "Name", "Mobile", "Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Step 2: Message ───────────────────────────────────────
    st.subheader("Step 2 — Compose Message")
    channel  = st.radio("Channel", ["SMS", "WhatsApp"], horizontal=True)

    template_names = list(templates.keys()) if templates else ["Custom"]
    template_sel   = st.selectbox("Template", template_names)
    default_msg    = templates.get(template_sel, "")

    message = st.text_area(
        "Message *", value=default_msg, height=120, max_chars=500,
        help="Use {name}, {programme}, {dept}, {date} as dynamic placeholders"
    )
    char_count = len(message)
    sms_count  = (char_count // 160) + 1
    st.caption(f"{char_count}/500 chars · ~{sms_count} SMS credit(s) per recipient")

    st.divider()

    # ── Step 3: Preview & Send ────────────────────────────────
    st.subheader("Step 3 — Preview & Send")
    if recipients and message.strip():
        sample = recipients[0]
        preview_msg = message \
            .replace("{name}",      sample["full_name"]) \
            .replace("{programme}", sample.get("programme_interested", "")) \
            .replace("{dept}",      sample.get("department_interested", "")) \
            .replace("{date}",      date.today().strftime("%d %b %Y"))
        st.markdown("**Preview (first recipient):**")
        st.info(preview_msg)

    st.warning(
        "⚠️ This module is ready for SMS/WhatsApp API integration "
        "(e.g. Twilio, MSG91, 2Factor). Add your API credentials in Settings & Admin → General."
    )

    col_send, col_export = st.columns(2)
    if col_send.button(
        f"🚀 Send {channel} to {len(recipients)} Recipient(s)",
        type="primary", use_container_width=True,
        disabled=not recipients or not message.strip()
    ):
        st.info("📡 SMS/WhatsApp API not yet configured — add credentials in Settings & Admin.")

    if recipients:
        df_exp = pd.DataFrame(recipients)[["full_name", "mobile", "status"]]
        csv    = df_exp.to_csv(index=False).encode("utf-8")
        col_export.download_button(
            "⬇️ Export Numbers (CSV)", csv, "recipients.csv", "text/csv",
            use_container_width=True
        )

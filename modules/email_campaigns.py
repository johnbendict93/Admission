"""Module 18 — Email Campaigns (100% dynamic — templates from Supabase)"""
import streamlit as st
import pandas as pd
import json
from datetime import date
from config import MAROON, GOLD, APPLICANT_STATUSES
from db import get_supabase, get_lookup


def load_email_templates(sb) -> dict:
    """Load email templates dynamically from settings table.
    Each row: key=template name, value=JSON {subject, body}
    """
    try:
        rows = sb.table("settings").select("key, value") \
            .eq("category", "email_template").eq("is_active", True) \
            .order("key").execute().data or []
        result = {}
        for r in rows:
            try:
                result[r["key"]] = json.loads(r["value"])
            except Exception:
                result[r["key"]] = {"subject": "", "body": r["value"]}
        return result
    except:
        return {"Custom": {"subject": "", "body": ""}}


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
        st.error(f"Error loading recipients: {e}")
        return []


def show():
    sb = get_supabase()
    DEPARTMENTS = get_lookup("department")
    templates   = load_email_templates(sb)

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>📧 Email Campaigns</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Send targeted email campaigns to applicant groups.
        </p>
    </div>""", unsafe_allow_html=True)

    # ── Audience ──────────────────────────────────────────────
    st.subheader("Audience")
    fc1, fc2 = st.columns(2)
    f_status = fc1.multiselect("By Status",     APPLICANT_STATUSES)
    f_dept   = fc2.multiselect("By Department", DEPARTMENTS)

    recipients = load_recipients(sb, f_status or None, f_dept or None)
    st.markdown(f"**{len(recipients)} recipient(s) with email addresses**")

    if recipients:
        with st.expander("Preview recipients"):
            df = pd.DataFrame(recipients)[["full_name", "email", "mobile", "status"]]
            df.columns = ["Name", "Email", "Mobile", "Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Compose ───────────────────────────────────────────────
    st.subheader("Compose Email")

    template_names = list(templates.keys()) if templates else ["Custom"]
    template_sel   = st.selectbox("Template", template_names)
    tpl            = templates.get(template_sel, {"subject": "", "body": ""})

    subject = st.text_input("Subject *", value=tpl.get("subject", ""))
    body    = st.text_area("Email Body *", value=tpl.get("body", ""), height=250,
                            help="Use {name}, {programme}, {date} as dynamic placeholders")

    if recipients and body.strip():
        sample = recipients[0]
        with st.expander("📄 Preview (first recipient)"):
            preview = body \
                .replace("{name}",      sample["full_name"]) \
                .replace("{programme}", sample.get("programme_interested", "")) \
                .replace("{date}",      date.today().strftime("%d %b %Y"))
            st.text(preview)

    st.divider()
    st.warning(
        "⚠️ Connect an SMTP / SendGrid / AWS SES account in Settings & Admin → General "
        "to enable actual sending."
    )

    col_send, col_export = st.columns(2)
    if col_send.button(
        f"📧 Send to {len(recipients)} Recipient(s)",
        type="primary", use_container_width=True,
        disabled=not recipients or not subject.strip() or not body.strip()
    ):
        st.info("Email API not configured — add SMTP/SendGrid credentials in Settings & Admin.")

    if recipients:
        df_exp = pd.DataFrame(recipients)[["full_name", "email", "mobile", "status"]]
        csv    = df_exp.to_csv(index=False).encode("utf-8")
        col_export.download_button(
            "⬇️ Export Email List (CSV)", csv, "email_list.csv", "text/csv",
            use_container_width=True
        )

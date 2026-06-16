"""Module 04 — Lead Tracker (searchable live table + inline status update)"""
import streamlit as st
import pandas as pd
from config import MAROON, GOLD, CREAM, APPLICANT_STATUSES
from db import get_supabase, get_lookup


STATUS_COLORS = {
    "New Lead":             "#3498DB",
    "Contacted":            "#9B59B6",
    "Interested":           "#27AE60",
    "Documents Pending":    "#E67E22",
    "Documents Submitted":  "#F39C12",
    "Counseled":            "#1ABC9C",
    "Confirmed":            "#2ECC71",
    "Fee Paid":             "#16A085",
    "Enrolled":             "#8B1A1A",
    "Not Interested":       "#95A5A6",
    "Dropped":              "#E74C3C",
}


def status_badge(status):
    color = STATUS_COLORS.get(status, "#888")
    return (f"<span style='background:{color};color:#fff;padding:2px 9px;"
            f"border-radius:12px;font-size:0.78rem;'>{status}</span>")


def load_leads(sb, filters):
    q = sb.table("applicants").select(
        "id, reg_number, full_name, mobile, email, "
        "programme_interested, department_interested, "
        "lead_source, status, created_at, notes"
    ).order("created_at", desc=True)

    if filters.get("status"):
        q = q.in_("status", filters["status"])
    if filters.get("department"):
        q = q.in_("department_interested", filters["department"])
    if filters.get("programme"):
        q = q.in_("programme_interested", filters["programme"])
    if filters.get("lead_source"):
        q = q.in_("lead_source", filters["lead_source"])

    try:
        rows = q.execute().data or []
        df = pd.DataFrame(rows)
        if not df.empty:
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d %b %Y")
        return df
    except Exception as e:
        st.error(f"Error loading leads: {e}")
        return pd.DataFrame()


def show():
    sb = get_supabase()
    DEPARTMENTS  = get_lookup('department')
    PROGRAMMES   = get_lookup('programme')
    LEAD_SOURCES = get_lookup('lead_source')

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🎯 Lead Tracker</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Search, filter, and update all leads in real-time.
        </p>
    </div>""", unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────
    with st.expander("🔍 Filters", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        f_status   = fc1.multiselect("Status",       APPLICANT_STATUSES)
        f_dept     = fc2.multiselect("Department",   DEPARTMENTS)
        f_prog     = fc3.multiselect("Programme",    PROGRAMMES)
        f_source   = fc4.multiselect("Lead Source",  LEAD_SOURCES)

    search = st.text_input("🔎 Search by name, mobile, or reg number",
                            placeholder="Type to search…")

    filters = {
        "status":      f_status,
        "department":  f_dept,
        "programme":   f_prog,
        "lead_source": f_source,
    }

    df = load_leads(sb, filters)

    # client-side search
    if search and not df.empty:
        s = search.lower()
        mask = (
            df["full_name"].str.lower().str.contains(s, na=False) |
            df["mobile"].str.lower().str.contains(s, na=False) |
            df["reg_number"].str.lower().str.contains(s, na=False)
        )
        df = df[mask]

    # ── Summary strip ─────────────────────────────────────────
    total = len(df)
    st.markdown(f"**{total} lead(s) found**")

    if df.empty:
        st.info("No leads match the current filters.")
        return

    # ── Table with inline status update ──────────────────────
    st.divider()

    # Render as styled HTML table (read-only) + separate update panel
    display_cols = ["reg_number", "full_name", "mobile",
                    "programme_interested", "department_interested",
                    "lead_source", "status", "created_at"]
    show_df = df[display_cols].copy()
    show_df.columns = ["Reg No", "Name", "Mobile", "Programme",
                       "Department", "Lead Source", "Status", "Registered"]

    st.dataframe(show_df, use_container_width=True, hide_index=True,
                 column_config={
                     "Status": st.column_config.SelectboxColumn(
                         "Status", options=APPLICANT_STATUSES, width="medium"
                     )
                 })

    st.divider()

    # ── Inline status update panel ────────────────────────────
    st.subheader("✏️ Update Lead Status")
    up_col1, up_col2, up_col3 = st.columns([2, 2, 1])

    reg_options = df["reg_number"].tolist()
    selected_reg = up_col1.selectbox("Select Reg No", reg_options)

    row = df[df["reg_number"] == selected_reg].iloc[0] if selected_reg else None
    current_status = row["status"] if row is not None else APPLICANT_STATUSES[0]

    new_status = up_col2.selectbox(
        "New Status",
        APPLICANT_STATUSES,
        index=APPLICANT_STATUSES.index(current_status)
        if current_status in APPLICANT_STATUSES else 0
    )

    note = st.text_input("Add note (optional)", placeholder="e.g. Called, interested in CSE")

    if up_col3.button("Update", type="primary", use_container_width=True):
        if row is not None:
            applicant_id = row["id"]
            payload = {"status": new_status}
            if note.strip():
                existing = row.get("notes") or ""
                from datetime import date
                payload["notes"] = (existing + f"\n[{date.today()}] {note.strip()}").strip()
            try:
                sb.table("applicants").update(payload).eq("id", applicant_id).execute()
                st.success(f"✅ {selected_reg} status updated to **{new_status}**")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")

    # ── Lead detail expander ──────────────────────────────────
    if row is not None:
        with st.expander(f"📄 Full Details — {row['full_name']} ({selected_reg})"):
            d1, d2 = st.columns(2)
            d1.markdown(f"**Mobile:** {row['mobile']}")
            d1.markdown(f"**Email:** {row.get('email') or '—'}")
            d1.markdown(f"**Programme:** {row['programme_interested']}")
            d1.markdown(f"**Department:** {row['department_interested']}")
            d2.markdown(f"**Lead Source:** {row['lead_source']}")
            d2.markdown(f"**Status:** {row['status']}")
            d2.markdown(f"**Registered:** {row['created_at']}")
            if row.get("notes"):
                st.markdown("**Notes:**")
                st.code(row["notes"], language=None)

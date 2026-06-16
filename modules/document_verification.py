"""Module 08 — Document Verification"""
import streamlit as st
import pandas as pd
from db import get_supabase
from config import MAROON, GOLD, CREAM

DOCUMENTS = [
    "10th Mark Sheet",
    "12th / HSC Mark Sheet",
    "Transfer Certificate (TC)",
    "Community Certificate",
    "Income Certificate",
    "Aadhar Card",
    "Passport Photo (4 copies)",
    "Conduct Certificate",
    "Migration Certificate (if applicable)",
    "Medical Fitness Certificate",
]

DOC_STATUS = ["Not Submitted", "Submitted", "Verified", "Rejected"]

STATUS_COLOR = {
    "Not Submitted": "#95A5A6",
    "Submitted":     "#F39C12",
    "Verified":      "#27AE60",
    "Rejected":      "#E74C3C",
}


def load_applicants(sb):
    try:
        rows = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, status"
        ).not_.in_("status", ["Dropped","Not Interested"])\
         .order("full_name").execute().data or []
        return rows
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def load_doc_status(sb, applicant_id):
    """Load existing doc verification from notes field (JSON-encoded section)."""
    try:
        row = sb.table("applicants").select("doc_status").eq("id", applicant_id).execute().data
        if row and row[0].get("doc_status"):
            import json
            return json.loads(row[0]["doc_status"])
    except:
        pass
    return {doc: "Not Submitted" for doc in DOCUMENTS}


def save_doc_status(sb, applicant_id, doc_data):
    import json
    try:
        sb.table("applicants").update(
            {"doc_status": json.dumps(doc_data)}
        ).eq("id", applicant_id).execute()
        return True
    except Exception as e:
        st.error(f"Save failed: {e}")
        return False


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>📋 Document Verification</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Track and verify documents submitted by each applicant.
        </p>
    </div>""", unsafe_allow_html=True)

    applicants = load_applicants(sb)
    if not applicants:
        st.info("No active applicants found.")
        return

    # ── Applicant selector ────────────────────────────────────
    options = {f"{a['reg_number']} — {a['full_name']}": a for a in applicants}
    col_sel, col_search = st.columns([3, 2])
    search = col_search.text_input("🔎 Search applicant", placeholder="Name or Reg No")
    if search:
        s = search.lower()
        options = {k: v for k, v in options.items() if s in k.lower()}

    if not options:
        st.warning("No matching applicants.")
        return

    chosen = col_sel.selectbox("Select Applicant", list(options.keys()))
    applicant = options[chosen]
    applicant_id = applicant["id"]

    st.markdown(f"**Status:** `{applicant['status']}` &nbsp;|&nbsp; "
                f"**Mobile:** {applicant['mobile']}")
    st.divider()

    # ── Document checklist ────────────────────────────────────
    doc_data = load_doc_status(sb, applicant_id)

    # Summary badges
    counts = {s: 0 for s in DOC_STATUS}
    for v in doc_data.values():
        counts[v] = counts.get(v, 0) + 1

    k1, k2, k3, k4 = st.columns(4)
    for col, label, key in [
        (k1, "Not Submitted", "Not Submitted"),
        (k2, "Submitted",     "Submitted"),
        (k3, "Verified",      "Verified"),
        (k4, "Rejected",      "Rejected"),
    ]:
        col.markdown(
            f"<div style='text-align:center;background:{STATUS_COLOR[key]}22;"
            f"border:1px solid {STATUS_COLOR[key]};border-radius:8px;padding:8px;'>"
            f"<b style='color:{STATUS_COLOR[key]};font-size:1.4rem;'>{counts[key]}</b>"
            f"<br><small>{label}</small></div>",
            unsafe_allow_html=True
        )

    st.divider()
    st.subheader("📁 Document Status")

    with st.form("doc_form"):
        new_data = {}
        for doc in DOCUMENTS:
            current = doc_data.get(doc, "Not Submitted")
            col_doc, col_status = st.columns([3, 2])
            col_doc.markdown(f"**{doc}**")
            new_status = col_status.selectbox(
                doc, DOC_STATUS,
                index=DOC_STATUS.index(current),
                key=f"doc_{doc}",
                label_visibility="collapsed"
            )
            new_data[doc] = new_status

        remarks = st.text_area("Verification Remarks (optional)",
                                placeholder="e.g. TC pending — student to bring by Friday")
        saved = st.form_submit_button("💾 Save Document Status", type="primary",
                                       use_container_width=True)

    if saved:
        if remarks.strip():
            new_data["_remarks"] = remarks.strip()
        if save_doc_status(sb, applicant_id, new_data):
            verified_count = sum(1 for k,v in new_data.items()
                                 if k != "_remarks" and v == "Verified")
            if verified_count == len(DOCUMENTS):
                # Auto-update status to Documents Submitted
                try:
                    sb.table("applicants").update(
                        {"status": "Documents Submitted"}
                    ).eq("id", applicant_id).execute()
                    st.success("✅ All documents verified! Applicant status updated to 'Documents Submitted'.")
                except:
                    st.success("✅ Document status saved.")
            else:
                st.success(f"✅ Saved. {verified_count}/{len(DOCUMENTS)} documents verified.")
            st.rerun()

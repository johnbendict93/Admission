"""Module 15 — Fee Management"""
import streamlit as st
import pandas as pd
from datetime import date
from db import get_supabase
from config import MAROON, GOLD, CREAM, DEPARTMENTS, PROGRAMMES

FEE_STRUCTURE = {
    ("B.E.",   "CSE"):   {"Tuition": 95000, "Special Fees": 15000, "Hostel": 65000},
    ("B.E.",   "ECE"):   {"Tuition": 90000, "Special Fees": 15000, "Hostel": 65000},
    ("B.E.",   "EEE"):   {"Tuition": 88000, "Special Fees": 15000, "Hostel": 65000},
    ("B.E.",   "MECH"):  {"Tuition": 85000, "Special Fees": 15000, "Hostel": 65000},
    ("B.E.",   "CIVIL"): {"Tuition": 82000, "Special Fees": 15000, "Hostel": 65000},
    ("B.Tech", "AIDS"):  {"Tuition": 98000, "Special Fees": 18000, "Hostel": 65000},
    ("B.Tech", "AIML"):  {"Tuition": 98000, "Special Fees": 18000, "Hostel": 65000},
    ("MBA",    "MBA"):   {"Tuition":120000, "Special Fees": 20000, "Hostel": 65000},
    ("MCA",    "MCA"):   {"Tuition":100000, "Special Fees": 18000, "Hostel": 65000},
}
DEFAULT_FEE = {"Tuition": 85000, "Special Fees": 15000, "Hostel": 65000}

PAYMENT_MODES = ["Cash","DD","Online Transfer","UPI","Cheque"]


def load_enrolled(sb):
    try:
        rows = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, "
            "programme_interested, department_interested, status"
        ).in_("status",["Confirmed","Fee Paid","Enrolled"])\
         .order("full_name").execute().data or []
        return {f"{r['reg_number']} — {r['full_name']}": r for r in rows}
    except:
        return {}


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>💰 Fee Management</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            View fee structure, record payments, track outstanding dues.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_structure, tab_payment = st.tabs(["📊 Fee Structure", "💳 Record Payment"])

    # ── Fee structure ─────────────────────────────────────────
    with tab_structure:
        st.subheader("Fee Structure (Annual) — 2026-27")
        fc1, fc2 = st.columns(2)
        sel_prog = fc1.selectbox("Programme", PROGRAMMES, key="fs_prog")
        sel_dept = fc2.selectbox("Department", DEPARTMENTS, key="fs_dept")

        fees = FEE_STRUCTURE.get((sel_prog, sel_dept), DEFAULT_FEE)
        total = sum(fees.values())

        fee_rows = [{"Component": k, "Amount (₹)": f"₹{v:,.0f}"} for k,v in fees.items()]
        fee_rows.append({"Component": "**TOTAL**", "Amount (₹)": f"**₹{total:,.0f}**"})
        st.table(pd.DataFrame(fee_rows))

        st.info(f"💡 Fee shown is annual. Students can pay in 2 instalments "
                f"(50% at admission, 50% before semester exam).")

    # ── Record payment ────────────────────────────────────────
    with tab_payment:
        enrolled = load_enrolled(sb)
        if not enrolled:
            st.info("No confirmed/enrolled applicants found.")
            return

        chosen = st.selectbox("Select Applicant", list(enrolled.keys()))
        applicant = enrolled[chosen]
        prog = applicant.get("programme_interested","")
        dept = applicant.get("department_interested","")
        fees = FEE_STRUCTURE.get((prog, dept), DEFAULT_FEE)
        total_fee = sum(fees.values())

        st.markdown(f"""
        <div style='background:{CREAM};border-left:4px solid {GOLD};
             padding:12px 16px;border-radius:8px;margin:12px 0;'>
            <b>{applicant['full_name']}</b> · {applicant['reg_number']}<br>
            {prog} — {dept} &nbsp;|&nbsp;
            Total Fee: <b>₹{total_fee:,.0f}</b>
        </div>""", unsafe_allow_html=True)

        with st.form("payment_form", clear_on_submit=True):
            pc1, pc2, pc3 = st.columns(3)
            fee_component = pc1.selectbox("Fee Component",
                                           list(fees.keys()) + ["Other"])
            amount_paid   = pc2.number_input("Amount Paid (₹)", min_value=1,
                                              max_value=200000, value=0, step=500)
            payment_mode  = pc3.selectbox("Payment Mode", PAYMENT_MODES)

            pd1, pd2 = st.columns(2)
            payment_date = pd1.date_input("Payment Date", value=date.today())
            receipt_no   = pd2.text_input("Receipt / Transaction No",
                                           placeholder="e.g. TXN123456")
            remarks = st.text_area("Remarks", height=60, placeholder="Optional notes")

            if st.form_submit_button("💾 Record Payment", type="primary",
                                      use_container_width=True):
                if amount_paid <= 0:
                    st.error("Enter a valid amount.")
                else:
                    # Store fee record in applicant notes (MVP — dedicated fee table later)
                    from datetime import datetime
                    note_entry = (
                        f"\n[FEE {payment_date}] {fee_component}: ₹{amount_paid:,} "
                        f"via {payment_mode} | Receipt: {receipt_no or 'N/A'}"
                        + (f" | {remarks.strip()}" if remarks.strip() else "")
                    )
                    try:
                        existing = sb.table("applicants").select("notes")\
                            .eq("id", applicant["id"]).execute().data
                        old_notes = (existing[0].get("notes") or "") if existing else ""
                        sb.table("applicants").update({
                            "notes":  old_notes + note_entry,
                            "status": "Fee Paid"
                        }).eq("id", applicant["id"]).execute()
                        st.success(f"✅ Payment of ₹{amount_paid:,} recorded for "
                                   f"{applicant['full_name']}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save: {e}")

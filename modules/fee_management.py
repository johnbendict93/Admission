"""Module 15 — Fee Management (proper fee_payments table)"""
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
    ("B.Tech", "CSD"):   {"Tuition": 98000, "Special Fees": 18000, "Hostel": 65000},
    ("B.E.",   "IT"):    {"Tuition": 92000, "Special Fees": 15000, "Hostel": 65000},
    ("MBA",    "MBA"):   {"Tuition":120000, "Special Fees": 20000, "Hostel": 65000},
    ("MCA",    "MCA"):   {"Tuition":100000, "Special Fees": 18000, "Hostel": 65000},
}
DEFAULT_FEE    = {"Tuition": 85000, "Special Fees": 15000, "Hostel": 65000}
PAYMENT_MODES  = ["Cash", "DD", "Online Transfer", "UPI", "Cheque"]


def load_enrolled(sb):
    try:
        rows = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, "
            "programme_interested, department_interested, status"
        ).in_("status", ["Confirmed", "Fee Paid", "Enrolled"])\
         .order("full_name").execute().data or []
        return {f"{r['reg_number']} — {r['full_name']}": r for r in rows}
    except:
        return {}


def load_payments(sb, applicant_id):
    try:
        rows = sb.table("fee_payments").select("*")\
            .eq("applicant_id", applicant_id)\
            .order("payment_date", desc=True).execute().data or []
        return rows
    except:
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>💰 Fee Management</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Record and track fee payments per student.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_structure, tab_payment, tab_history = st.tabs(
        ["📊 Fee Structure", "💳 Record Payment", "📋 Payment History"])

    # ── Tab 1: Fee structure ──────────────────────────────────
    with tab_structure:
        st.subheader("Fee Structure (Annual) — 2026-27")
        fc1, fc2 = st.columns(2)
        sel_prog = fc1.selectbox("Programme", PROGRAMMES, key="fs_prog")
        sel_dept = fc2.selectbox("Department", DEPARTMENTS, key="fs_dept")

        fees  = FEE_STRUCTURE.get((sel_prog, sel_dept), DEFAULT_FEE)
        total = sum(fees.values())

        rows = [{"Component": k, "Amount (₹)": f"₹{v:,.0f}"} for k, v in fees.items()]
        rows.append({"Component": "TOTAL", "Amount (₹)": f"₹{total:,.0f}"})
        st.table(pd.DataFrame(rows))
        st.info("Payable in 2 instalments — 50% at admission, 50% before semester exam.")

    # ── Tab 2: Record payment ─────────────────────────────────
    with tab_payment:
        enrolled = load_enrolled(sb)
        if not enrolled:
            st.info("No confirmed/enrolled applicants found.")
            return

        chosen    = st.selectbox("Select Student", list(enrolled.keys()), key="fp_sel")
        applicant = enrolled[chosen]
        prog      = applicant.get("programme_interested", "")
        dept      = applicant.get("department_interested", "")
        fees      = FEE_STRUCTURE.get((prog, dept), DEFAULT_FEE)
        total_fee = sum(fees.values())

        # Show existing payments summary
        payments = load_payments(sb, applicant["id"])
        paid_total = sum(p["amount"] for p in payments)
        outstanding = total_fee - paid_total

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Fee",   f"₹{total_fee:,.0f}")
        k2.metric("Paid",        f"₹{paid_total:,.0f}")
        k3.metric("Outstanding", f"₹{outstanding:,.0f}",
                  delta=f"-₹{outstanding:,.0f}" if outstanding > 0 else "Cleared ✅",
                  delta_color="inverse")

        st.divider()
        with st.form("payment_form", clear_on_submit=True):
            pc1, pc2, pc3 = st.columns(3)
            fee_component = pc1.selectbox("Fee Component",
                                           list(fees.keys()) + ["Other"])
            amount_paid   = pc2.number_input("Amount (₹)", min_value=1,
                                              max_value=200000, value=0, step=500)
            payment_mode  = pc3.selectbox("Payment Mode", PAYMENT_MODES)

            pd1, pd2 = st.columns(2)
            payment_date = pd1.date_input("Payment Date", value=date.today())
            receipt_no   = pd2.text_input("Receipt / Transaction No")
            remarks      = st.text_area("Remarks", height=60)

            if st.form_submit_button("💾 Record Payment", type="primary",
                                      use_container_width=True):
                if amount_paid <= 0:
                    st.error("Enter a valid amount.")
                else:
                    try:
                        sb.table("fee_payments").insert({
                            "applicant_id":  applicant["id"],
                            "fee_component": fee_component,
                            "amount":        float(amount_paid),
                            "payment_mode":  payment_mode,
                            "payment_date":  payment_date.isoformat(),
                            "receipt_no":    receipt_no.strip() or None,
                            "academic_year": "2026-27",
                            "remarks":       remarks.strip() or None,
                        }).execute()
                        # Update status to Fee Paid
                        sb.table("applicants").update({"status": "Fee Paid"})\
                            .eq("id", applicant["id"]).execute()
                        st.success(f"✅ ₹{amount_paid:,} recorded for {applicant['full_name']}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")

    # ── Tab 3: Payment history ────────────────────────────────
    with tab_history:
        enrolled2  = load_enrolled(sb)
        chosen2    = st.selectbox("Student", list(enrolled2.keys()), key="fh_sel")
        applicant2 = enrolled2.get(chosen2, {})

        if not applicant2:
            st.info("Select a student.")
            return

        payments2 = load_payments(sb, applicant2["id"])
        if not payments2:
            st.info("No payments recorded yet for this student.")
        else:
            df = pd.DataFrame(payments2)[[
                "payment_date","fee_component","amount",
                "payment_mode","receipt_no","remarks"]]
            df.columns = ["Date","Component","Amount (₹)","Mode","Receipt","Remarks"]
            df["Amount (₹)"] = df["Amount (₹)"].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(df, use_container_width=True, hide_index=True)

            total_paid = sum(p["amount"] for p in payments2)
            st.markdown(f"**Total Paid: ₹{total_paid:,.0f}**")

            csv = pd.DataFrame(payments2).to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export (CSV)", csv,
                               f"fees_{applicant2['reg_number']}.csv", "text/csv")

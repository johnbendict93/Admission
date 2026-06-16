"""Module 16 — Scholarship Management"""
import streamlit as st
import pandas as pd
from db import get_supabase
from config import MAROON, GOLD, CREAM, DEPARTMENTS, CATEGORIES

SCHOLARSHIP_TYPES = [
    "Government Scholarship (SC/ST)",
    "BC/MBC Scholarship",
    "Merit Scholarship",
    "Sports Quota",
    "Management Scholarship",
    "Minority Scholarship",
    "Fee Concession",
    "Other",
]
SCHOLARSHIP_STATUS = ["Applied","Under Review","Approved","Disbursed","Rejected"]


def load_applicants(sb):
    try:
        rows = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, category, "
            "hsc_percentage, programme_interested, department_interested, status"
        ).in_("status",["Confirmed","Fee Paid","Enrolled"])\
         .order("full_name").execute().data or []
        return rows
    except:
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🎓 Scholarship Management</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Track government and management scholarships for enrolled students.
        </p>
    </div>""", unsafe_allow_html=True)

    applicants = load_applicants(sb)

    tab_apply, tab_status = st.tabs(["➕ Add Scholarship", "📋 Scholarship Status"])

    with tab_apply:
        if not applicants:
            st.info("No confirmed/enrolled students yet.")
        else:
            options = {f"{a['reg_number']} — {a['full_name']}": a for a in applicants}
            with st.form("scholar_form", clear_on_submit=True):
                chosen  = st.selectbox("Student *", list(options.keys()))
                student = options.get(chosen, {})

                if student:
                    st.markdown(
                        f"**Category:** {student.get('category','—')} &nbsp;|&nbsp; "
                        f"**HSC %:** {student.get('hsc_percentage','—')} &nbsp;|&nbsp; "
                        f"**Programme:** {student.get('programme_interested','—')} — "
                        f"{student.get('department_interested','—')}"
                    )

                sc1, sc2 = st.columns(2)
                sch_type   = sc1.selectbox("Scholarship Type *", SCHOLARSHIP_TYPES)
                sch_amount = sc2.number_input("Scholarship Amount (₹)",
                                               min_value=0, max_value=500000,
                                               step=1000, value=0)
                sc3, sc4 = st.columns(2)
                sch_year   = sc3.text_input("Academic Year", value="2026-27")
                sch_status = sc4.selectbox("Status", SCHOLARSHIP_STATUS)
                ref_no     = st.text_input("Application / Reference No",
                                            placeholder="e.g. TNGOVT-2026-XXXXX")
                remarks    = st.text_area("Remarks", height=68)

                if st.form_submit_button("💾 Save Scholarship Record",
                                          type="primary", use_container_width=True):
                    if not student:
                        st.error("Select a student.")
                    else:
                        from datetime import date
                        note = (
                            f"\n[SCHOLARSHIP {date.today()}] {sch_type} | "
                            f"₹{sch_amount:,} | {sch_year} | Status: {sch_status}"
                            + (f" | Ref: {ref_no}" if ref_no.strip() else "")
                            + (f" | {remarks.strip()}" if remarks.strip() else "")
                        )
                        try:
                            existing = sb.table("applicants").select("notes")\
                                .eq("id", student["id"]).execute().data
                            old = (existing[0].get("notes") or "") if existing else ""
                            sb.table("applicants").update({"notes": old + note})\
                                .eq("id", student["id"]).execute()
                            st.success(f"✅ Scholarship record saved for {student['full_name']}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

    with tab_status:
        st.subheader("Students by Category")
        if not applicants:
            st.info("No enrolled students yet.")
            return

        df = pd.DataFrame(applicants)
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category","Count"]
        st.dataframe(cat_counts, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Likely Eligible for Government Scholarship")
        govt_cats = ["SC","SCA","ST","BC","BCM","MBC"]
        eligible = df[df["category"].isin(govt_cats)][
            ["reg_number","full_name","mobile","category",
             "hsc_percentage","programme_interested","department_interested"]
        ].rename(columns={
            "reg_number":"Reg No","full_name":"Name","mobile":"Mobile",
            "category":"Category","hsc_percentage":"HSC %",
            "programme_interested":"Programme","department_interested":"Department"
        })
        if eligible.empty:
            st.info("No SC/ST/BC/MBC students in the enrolled list.")
        else:
            st.dataframe(eligible, use_container_width=True, hide_index=True)
            csv = eligible.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export Eligible List (CSV)", csv,
                               "scholarship_eligible.csv","text/csv")

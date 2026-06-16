"""Module 16 — Scholarship Management (proper scholarships table)"""
import streamlit as st
import pandas as pd
from config import MAROON, GOLD, CREAM
from db import get_supabase, get_lookup, get_academic_year


def load_enrolled(sb):
    try:
        rows = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, category, "
            "hsc_percentage, programme_interested, department_interested"
        ).in_("status", ["Confirmed", "Fee Paid", "Enrolled"])\
         .order("full_name").execute().data or []
        return rows
    except:
        return []


def load_scholarships(sb, applicant_id=None):
    try:
        q = sb.table("scholarships").select(
            "*, applicants(reg_number, full_name, category)"
        ).order("created_at", desc=True)
        if applicant_id:
            q = q.eq("applicant_id", applicant_id)
        return q.execute().data or []
    except:
        return []


def show():
    sb = get_supabase()
    SCHOLARSHIP_TYPES  = get_lookup('scholarship_type')
    SCHOLARSHIP_STATUS = get_lookup('scholarship_status') or ['Applied','Under Review','Approved','Disbursed','Rejected']
    CATEGORIES         = get_lookup('category')
    GOVT_CATS          = get_lookup('govt_category') or ['SC','SCA','ST','BC','BCM','MBC']

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🎓 Scholarship Management</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Track government and management scholarships for enrolled students.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_add, tab_tracker, tab_eligible = st.tabs(
        ["➕ Add Record", "📋 All Scholarships", "🏷️ Eligible Students"])

    enrolled = load_enrolled(sb)

    # ── Tab 1: Add record ─────────────────────────────────────
    with tab_add:
        if not enrolled:
            st.info("No confirmed/enrolled students yet.")
        else:
            options = {f"{s['reg_number']} — {s['full_name']}": s for s in enrolled}
            with st.form("scholar_form", clear_on_submit=True):
                chosen  = st.selectbox("Student *", list(options.keys()))
                student = options.get(chosen, {})

                if student:
                    st.markdown(
                        f"**Category:** {student.get('category') or '—'} &nbsp;|&nbsp;"
                        f"**HSC %:** {student.get('hsc_percentage') or '—'} &nbsp;|&nbsp;"
                        f"**Programme:** {student.get('programme_interested','')} — "
                        f"{student.get('department_interested','')}"
                    )

                sc1, sc2 = st.columns(2)
                sch_type   = sc1.selectbox("Scholarship Type *", SCHOLARSHIP_TYPES)
                sch_amount = sc2.number_input("Amount (₹)", min_value=0,
                                               max_value=500000, step=500, value=0)
                sc3, sc4 = st.columns(2)
                sch_year   = sc3.text_input("Academic Year", value=get_academic_year())
                sch_status = sc4.selectbox("Status", SCHOLARSHIP_STATUS)
                ref_no     = st.text_input("Application / Reference No",
                                            placeholder="e.g. TNGOVT-2026-XXXXX")
                remarks    = st.text_area("Remarks", height=60)

                if st.form_submit_button("💾 Save Record", type="primary",
                                          use_container_width=True):
                    if not student:
                        st.error("Select a student.")
                    else:
                        try:
                            sb.table("scholarships").insert({
                                "applicant_id":     student["id"],
                                "scholarship_type": sch_type,
                                "amount":           float(sch_amount),
                                "academic_year":    sch_year.strip(),
                                "status":           sch_status,
                                "reference_no":     ref_no.strip() or None,
                                "remarks":          remarks.strip() or None,
                            }).execute()
                            st.success(f"✅ Scholarship record saved for {student['full_name']}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

    # ── Tab 2: All scholarships ───────────────────────────────
    with tab_tracker:
        records = load_scholarships(sb)
        if not records:
            st.info("No scholarship records yet.")
        else:
            STATUS_COLOR = {
                "Applied": "#3498DB", "Under Review": "#F39C12",
                "Approved": "#27AE60", "Disbursed": "#16A085", "Rejected": "#E74C3C",
            }
            rows = []
            for r in records:
                appl = r.get("applicants") or {}
                rows.append({
                    "Name":    appl.get("full_name","—") if isinstance(appl,dict) else "—",
                    "Reg No":  appl.get("reg_number","") if isinstance(appl,dict) else "",
                    "Category":appl.get("category","")   if isinstance(appl,dict) else "",
                    "Type":    r["scholarship_type"],
                    "Amount":  f"₹{r['amount']:,.0f}",
                    "Status":  r["status"],
                    "Ref No":  r.get("reference_no") or "—",
                    "Year":    r.get("academic_year",""),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            total_disbursed = sum(
                r["amount"] for r in records if r["status"] == "Disbursed")
            total_approved  = sum(
                r["amount"] for r in records if r["status"] in ["Approved","Disbursed"])
            k1, k2, k3 = st.columns(3)
            k1.metric("Total Records",    len(records))
            k2.metric("Total Approved",   f"₹{total_approved:,.0f}")
            k3.metric("Total Disbursed",  f"₹{total_disbursed:,.0f}")

    # ── Tab 3: Eligible students ──────────────────────────────
    with tab_eligible:
        st.subheader("Government Scholarship Eligible (SC/ST/BC/MBC)")
        eligible = [s for s in enrolled if s.get("category") in GOVT_CATS]
        if not eligible:
            st.info("No SC/ST/BC/MBC students in enrolled list yet.")
        else:
            df_el = pd.DataFrame(eligible)[[
                "reg_number","full_name","mobile","category",
                "hsc_percentage","programme_interested","department_interested"]]
            df_el.columns = ["Reg No","Name","Mobile","Category",
                             "HSC %","Programme","Department"]
            st.dataframe(df_el, use_container_width=True, hide_index=True)
            csv = df_el.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export CSV", csv,
                file_name="eligible_scholarship_students.csv", mime="text/csv")

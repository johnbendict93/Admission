"""Module 03 — Walk-in Registration (100% dynamic from Supabase)"""
import streamlit as st
from datetime import date
from db import get_supabase, get_lookup, get_applicant_statuses
from config import MAROON, GOLD


def show():
    sb = get_supabase()

    # Load all dropdowns dynamically
    programmes   = get_lookup("programme")
    departments  = get_lookup("department")
    categories   = get_lookup("category")
    lead_sources = get_lookup("lead_source")
    genders      = get_lookup("gender")
    blood_groups = get_lookup("blood_group")

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:#C9A84C;margin:0;'>🚶 Walk-in Registration</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Register a new walk-in enquiry — inserted live into Supabase.
        </p>
    </div>""", unsafe_allow_html=True)

    with st.expander("📋 Recent Registrations (last 10)", expanded=False):
        try:
            rows = sb.table("applicants").select(
                "reg_number, full_name, mobile, programme_interested, status, created_at"
            ).order("created_at", desc=True).limit(10).execute().data or []
            if rows:
                import pandas as pd
                df = pd.DataFrame(rows)
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d %b %Y %H:%M")
                df.columns = ["Reg No","Name","Mobile","Programme","Status","Registered At"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No registrations yet.")
        except Exception as e:
            st.warning(f"Could not load recent records: {e}")

    st.divider()

    with st.form("walkin_form", clear_on_submit=True):
        st.subheader("👤 Personal Information")
        c1, c2, c3 = st.columns(3)
        full_name   = c1.text_input("Full Name *", placeholder="e.g. Priya Rajan")
        dob         = c2.date_input("Date of Birth", value=None,
                                     min_value=date(1990,1,1), max_value=date(2010,12,31))
        gender      = c3.selectbox("Gender", [""]+genders)

        c4, c5, c6 = st.columns(3)
        mobile      = c4.text_input("Mobile Number *", placeholder="10-digit mobile")
        email       = c5.text_input("Email", placeholder="optional")
        blood_group = c6.selectbox("Blood Group", [""]+blood_groups)

        c7, c8 = st.columns(2)
        father_name = c7.text_input("Father's Name")
        mother_name = c8.text_input("Mother's Name")
        father_mob  = c7.text_input("Father's Mobile")
        address     = st.text_area("Address", height=68)

        st.divider()
        st.subheader("🎓 Academic & Programme Interest")
        ca, cb, cc = st.columns(3)
        programme   = ca.selectbox("Programme Interested *", [""]+programmes)
        department  = cb.selectbox("Department / Branch *",  [""]+departments)
        category    = cc.selectbox("Quota / Category",       [""]+categories)

        cd, ce = st.columns(2)
        hsc_percent = cd.number_input("12th / HSC %", min_value=0.0,
                                       max_value=100.0, step=0.1, value=None)
        school_name = ce.text_input("School / College Name")

        st.divider()
        st.subheader("📡 Lead Source")
        cf, cg = st.columns(2)
        lead_source = cf.selectbox("How did they hear about DCE? *", [""]+lead_sources)
        ref_name    = cg.text_input("Reference Name (if referred)")
        notes       = st.text_area("Counselor Notes", height=80)

        submitted = st.form_submit_button("✅ Register Walk-in",
                                          use_container_width=True, type="primary")

    if submitted:
        errors = []
        if not full_name.strip():
            errors.append("Full Name is required.")
        if not mobile.strip() or not mobile.strip().isdigit() or len(mobile.strip()) != 10:
            errors.append("Valid 10-digit Mobile Number is required.")
        if not programme:
            errors.append("Programme Interested is required.")
        if not department:
            errors.append("Department / Branch is required.")
        if not lead_source:
            errors.append("Lead Source is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            payload = {
                "full_name":             full_name.strip(),
                "mobile":                mobile.strip(),
                "email":                 email.strip() or None,
                "gender":                gender or None,
                "dob":                   dob.isoformat() if dob else None,
                "blood_group":           blood_group or None,
                "father_name":           father_name.strip() or None,
                "mother_name":           mother_name.strip() or None,
                "father_mobile":         father_mob.strip() or None,
                "address":               address.strip() or None,
                "programme_interested":  programme,
                "department_interested": department,
                "category":              category or None,
                "hsc_percentage":        float(hsc_percent) if hsc_percent is not None else None,
                "school_name":           school_name.strip() or None,
                "lead_source":           lead_source,
                "reference_name":        ref_name.strip() or None,
                "notes":                 notes.strip() or None,
                "status":                "New Lead",
            }
            try:
                result = sb.table("applicants").insert(payload).execute()
                data   = result.data[0] if result.data else {}
                reg_no = data.get("reg_number", "—")
                st.success(f"✅ Walk-in registered! Registration No: **{reg_no}**")
                st.balloons()
                st.markdown(f"""
                <div style='background:#F5F0E8;border-left:4px solid #C9A84C;
                     padding:14px 18px;border-radius:8px;margin-top:12px;'>
                    <b>Name:</b> {full_name} &nbsp;|&nbsp;
                    <b>Mobile:</b> {mobile} &nbsp;|&nbsp;
                    <b>Programme:</b> {programme} – {department}<br>
                    <b>Lead Source:</b> {lead_source} &nbsp;|&nbsp;
                    <b>Status:</b> New Lead &nbsp;|&nbsp;
                    <b>Reg No:</b> {reg_no}
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Insert failed: {e}")

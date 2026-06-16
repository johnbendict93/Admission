"""Module 14 — Seat Allotment"""
import streamlit as st
import pandas as pd
from config import MAROON, GOLD, CREAM
from db import get_supabase, get_lookup, get_seat_intake


def load_allotment_summary(sb):
    try:
        rows = sb.table("applications").select(
            "department, application_stage, category"
        ).execute().data or []
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()


def load_merit_applicants(sb, dept, programme):
    try:
        rows = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, hsc_percentage, category, status"
        ).eq("department_interested", dept)\
         .eq("programme_interested", programme)\
         .not_.in_("status", ["Dropped","Not Interested","Enrolled"])\
         .not_.is_("hsc_percentage","null")\
         .order("hsc_percentage", desc=True)\
         .execute().data or []
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()


def show():
    sb = get_supabase()
    SEAT_INTAKE  = get_seat_intake()
    DEPARTMENTS  = get_lookup('department')
    PROGRAMMES   = get_lookup('programme')
    CATEGORIES   = get_lookup('category')

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🪑 Seat Allotment</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            View seat availability and allot seats to qualified applicants.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_overview, tab_allot = st.tabs(["📊 Seat Overview", "🪑 Allot Seats"])

    with tab_overview:
        df = load_allotment_summary(sb)

        st.subheader("Department-wise Seat Status")
        rows = []
        for dept, intake in SEAT_INTAKE.items():
            if df.empty:
                filled = 0
            else:
                dept_df = df[df["department"] == dept]
                filled  = len(dept_df[dept_df["application_stage"].isin(
                    ["Seat Allotted","Fee Paid","Enrolled"])])
            available = intake - filled
            pct = round(filled / intake * 100, 1) if intake else 0
            rows.append({
                "Department": dept,
                "Total Seats": intake,
                "Filled": filled,
                "Available": available,
                "Fill %": pct,
            })
        summary_df = pd.DataFrame(rows)

        def color_fill(val):
            if val >= 90: return "background-color:#E74C3C22;color:#E74C3C"
            if val >= 70: return "background-color:#F39C1222;color:#F39C12"
            return "background-color:#27AE6022;color:#27AE60"

        st.dataframe(
            summary_df.style.applymap(color_fill, subset=["Fill %"]),
            use_container_width=True, hide_index=True
        )

        # Summary KPIs
        total_seats = sum(SEAT_INTAKE.values())
        total_filled = summary_df["Filled"].sum()
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Seats", total_seats)
        k2.metric("Filled", int(total_filled))
        k3.metric("Available", int(total_seats - total_filled))

    with tab_allot:
        st.subheader("Allot Seat to Applicant")
        ac1, ac2 = st.columns(2)
        programme  = ac1.selectbox("Programme", PROGRAMMES)
        department = ac2.selectbox("Department", DEPARTMENTS)

        merit_df = load_merit_applicants(sb, department, programme)

        if merit_df.empty:
            st.info(f"No eligible applicants for {programme} — {department}.")
        else:
            intake    = SEAT_INTAKE.get(department, 60)
            allotted_count = 0
            try:
                allotted_count = sb.table("applications").select("id", count="exact")\
                    .eq("department", department)\
                    .in_("application_stage",["Seat Allotted","Fee Paid","Enrolled"])\
                    .execute().count or 0
            except:
                pass
            available = intake - allotted_count
            st.info(f"**{available}** seat(s) available in {department} "
                    f"(Intake: {intake}, Filled: {allotted_count})")

            merit_df.index = range(1, len(merit_df)+1)
            merit_df.index.name = "Rank"
            show_cols = ["reg_number","full_name","mobile","hsc_percentage","category","status"]
            st.dataframe(merit_df[show_cols].rename(columns={
                "reg_number":"Reg No","full_name":"Name","mobile":"Mobile",
                "hsc_percentage":"HSC %","category":"Category","status":"Status"
            }), use_container_width=True)

            st.divider()
            reg_options = merit_df["reg_number"].tolist()
            sel_reg = st.selectbox("Select Applicant to Allot Seat", reg_options)
            sel_row = merit_df[merit_df["reg_number"]==sel_reg].iloc[0] if sel_reg else None

            if sel_row is not None and st.button("🪑 Allot Seat", type="primary"):
                if available <= 0:
                    st.error("No seats available in this department.")
                else:
                    try:
                        # Update applicant status
                        sb.table("applicants").update({"status":"Confirmed"})\
                            .eq("id", sel_row["id"]).execute()
                        # Create/update application stage
                        existing = sb.table("applications").select("id")\
                            .eq("applicant_id", sel_row["id"])\
                            .eq("department", department).execute().data
                        if existing:
                            sb.table("applications").update(
                                {"application_stage":"Seat Allotted"}
                            ).eq("id", existing[0]["id"]).execute()
                        else:
                            sb.table("applications").insert({
                                "applicant_id":      sel_row["id"],
                                "programme":         programme,
                                "department":        department,
                                "category":          sel_row.get("category"),
                                "application_stage": "Seat Allotted",
                            }).execute()
                        st.success(f"✅ Seat allotted to {sel_row['full_name']} ({sel_reg})!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")

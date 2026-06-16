"""Module 13 — Application Tracker"""
import streamlit as st
import pandas as pd
from datetime import date
from db import get_supabase
from config import MAROON, GOLD, CREAM, DEPARTMENTS, PROGRAMMES, CATEGORIES

APP_STAGES = [
    "Form Submitted", "Documents Uploaded", "Under Review",
    "Merit Listed", "Seat Allotted", "Fee Paid", "Enrolled", "Rejected"
]


def load_applications(sb, search="", stage_filter=None, dept_filter=None):
    try:
        q = sb.table("applications").select(
            "id, application_no, programme, department, application_stage, "
            "category, created_at, applicant_id, "
            "applicants(reg_number, full_name, mobile)"
        ).order("created_at", desc=True)
        if stage_filter:
            q = q.in_("application_stage", stage_filter)
        if dept_filter:
            q = q.in_("department", dept_filter)
        rows = q.execute().data or []
        df = pd.DataFrame(rows)
        if not df.empty:
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d %b %Y")
            # Flatten nested applicant info
            df["full_name"] = df["applicants"].apply(
                lambda x: x.get("full_name","—") if isinstance(x,dict) else "—")
            df["mobile"] = df["applicants"].apply(
                lambda x: x.get("mobile","") if isinstance(x,dict) else "")
            df["reg_number"] = df["applicants"].apply(
                lambda x: x.get("reg_number","") if isinstance(x,dict) else "")
            if search:
                s = search.lower()
                df = df[
                    df["full_name"].str.lower().str.contains(s, na=False) |
                    df["application_no"].str.lower().str.contains(s, na=False) |
                    df["reg_number"].str.lower().str.contains(s, na=False)
                ]
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()


def load_applicants(sb):
    try:
        rows = sb.table("applicants").select("id, reg_number, full_name")\
            .not_.in_("status",["Dropped","Not Interested"])\
            .order("full_name").execute().data or []
        return {f"{r['reg_number']} — {r['full_name']}": r["id"] for r in rows}
    except:
        return {}


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>📝 Application Tracker</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Track every application through the admission pipeline.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_list, tab_new = st.tabs(["📋 All Applications", "➕ New Application"])

    with tab_list:
        fc1, fc2, fc3 = st.columns(3)
        search     = fc1.text_input("🔎 Search", placeholder="Name / App No / Reg No")
        f_stage    = fc2.multiselect("Stage", APP_STAGES)
        f_dept     = fc3.multiselect("Department", DEPARTMENTS)

        df = load_applications(sb, search, f_stage or None, f_dept or None)

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        enrolled = len(df[df["application_stage"]=="Enrolled"]) if not df.empty else 0
        allotted = len(df[df["application_stage"]=="Seat Allotted"]) if not df.empty else 0
        for col, icon, val, label in [
            (k1,"📝",len(df),       "Total Applications"),
            (k2,"🪑",allotted,      "Seat Allotted"),
            (k3,"✅",enrolled,      "Enrolled"),
            (k4,"📊",len(df[df["application_stage"]=="Under Review"]) if not df.empty else 0, "Under Review"),
        ]:
            with col:
                st.markdown(f'<div class="metric-card"><h3>{icon} {val}</h3><p>{label}</p></div>',
                            unsafe_allow_html=True)

        st.divider()

        if df.empty:
            st.info("No applications found.")
        else:
            show_df = df[["application_no","full_name","mobile","programme",
                          "department","category","application_stage","created_at"]].copy()
            show_df.columns = ["App No","Name","Mobile","Programme",
                               "Department","Category","Stage","Applied On"]
            st.dataframe(show_df, use_container_width=True, hide_index=True)

            # Inline stage update
            st.divider()
            st.subheader("✏️ Update Application Stage")
            uc1, uc2, uc3 = st.columns([3,2,1])
            app_options = df["application_no"].tolist()
            sel_app = uc1.selectbox("Application No", app_options)
            sel_row = df[df["application_no"]==sel_app].iloc[0] if sel_app else None
            cur_stage = sel_row["application_stage"] if sel_row is not None else APP_STAGES[0]
            new_stage = uc2.selectbox("New Stage", APP_STAGES,
                                       index=APP_STAGES.index(cur_stage) if cur_stage in APP_STAGES else 0)
            if uc3.button("Update", type="primary", use_container_width=True):
                if sel_row is not None:
                    try:
                        sb.table("applications").update({"application_stage": new_stage})\
                            .eq("id", sel_row["id"]).execute()
                        st.success(f"✅ {sel_app} stage updated to {new_stage}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")

    with tab_new:
        applicants = load_applicants(sb)
        with st.form("new_app_form", clear_on_submit=True):
            chosen = st.selectbox("Applicant *", ["—"] + list(applicants.keys()))
            nc1, nc2, nc3 = st.columns(3)
            programme = nc1.selectbox("Programme *", PROGRAMMES)
            department = nc2.selectbox("Department *", DEPARTMENTS)
            category  = nc3.selectbox("Category", [""] + CATEGORIES)
            stage     = st.selectbox("Initial Stage", APP_STAGES)
            remarks   = st.text_area("Remarks", height=60)

            if st.form_submit_button("Submit Application", type="primary",
                                      use_container_width=True):
                if chosen == "—":
                    st.error("Select an applicant.")
                else:
                    payload = {
                        "applicant_id":      applicants[chosen],
                        "programme":         programme,
                        "department":        department,
                        "category":          category or None,
                        "application_stage": stage,
                        "remarks":           remarks.strip() or None,
                    }
                    try:
                        result = sb.table("applications").insert(payload).execute()
                        app_no = result.data[0].get("application_no","—") if result.data else "—"
                        st.success(f"✅ Application {app_no} created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")

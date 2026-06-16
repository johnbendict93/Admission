"""Module 20 — Hostel Allotment"""
import streamlit as st
import pandas as pd
from db import get_supabase
from config import MAROON, GOLD, CREAM

BLOCKS = {
    "A Block (Boys)":   {"capacity": 120, "gender": "Male"},
    "B Block (Boys)":   {"capacity": 100, "gender": "Male"},
    "C Block (Girls)":  {"capacity": 150, "gender": "Female"},
    "D Block (Girls)":  {"capacity": 100, "gender": "Female"},
}
ROOM_TYPES = ["Single", "Double", "Triple"]


def load_enrolled(sb, gender=None):
    try:
        q = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, gender, "
            "programme_interested, department_interested, status"
        ).in_("status", ["Confirmed","Fee Paid","Enrolled"])
        if gender:
            q = q.eq("gender", gender)
        rows = q.order("full_name").execute().data or []
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()


def load_allotments(sb):
    """Read hostel allotments stored in applicant notes."""
    try:
        rows = sb.table("applicants").select(
            "reg_number, full_name, gender, notes"
        ).in_("status",["Confirmed","Fee Paid","Enrolled"])\
         .not_.is_("notes","null").execute().data or []
        allotted = []
        for r in rows:
            if "[HOSTEL]" in (r.get("notes") or ""):
                for line in (r["notes"] or "").split("\n"):
                    if "[HOSTEL]" in line:
                        allotted.append({
                            "Reg No":     r["reg_number"],
                            "Name":       r["full_name"],
                            "Gender":     r["gender"],
                            "Details":    line.replace("[HOSTEL]","").strip(),
                        })
        return allotted
    except:
        return []


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🏠 Hostel Allotment</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Manage hostel block and room allotment for enrolled students.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_overview, tab_allot, tab_list = st.tabs(
        ["📊 Block Overview", "🛏️ Allot Room", "📋 Allotted Students"])

    with tab_overview:
        st.subheader("Block-wise Capacity")
        allotted_list = load_allotments(sb)
        rows = []
        for block, info in BLOCKS.items():
            allotted = sum(1 for a in allotted_list if block in a.get("Details",""))
            rows.append({
                "Block": block,
                "Capacity": info["capacity"],
                "Allotted": allotted,
                "Available": info["capacity"] - allotted,
                "Gender": info["gender"],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Hostel Capacity", sum(b["capacity"] for b in BLOCKS.values()))
        k2.metric("Allotted", len(allotted_list))
        k3.metric("Available", sum(b["capacity"] for b in BLOCKS.values()) - len(allotted_list))

    with tab_allot:
        gender_filter = st.radio("Gender", ["Male","Female"], horizontal=True)
        block_options = [b for b,i in BLOCKS.items() if i["gender"] == gender_filter]
        sel_block = st.selectbox("Block", block_options)
        room_type = st.selectbox("Room Type", ROOM_TYPES)
        room_no   = st.text_input("Room Number", placeholder="e.g. A-101")

        enrolled_df = load_enrolled(sb, gender_filter)
        if enrolled_df.empty:
            st.info(f"No {gender_filter} students in Confirmed/Enrolled status.")
        else:
            options = {f"{r['reg_number']} — {r['full_name']}": r
                       for _, r in enrolled_df.iterrows()}
            chosen = st.selectbox("Student", list(options.keys()))
            student = options.get(chosen, {})

            if st.button("🛏️ Allot Room", type="primary") and student and room_no.strip():
                from datetime import date
                note = (f"\n[HOSTEL] Block: {sel_block} | Room: {room_no} | "
                        f"Type: {room_type} | Date: {date.today()}")
                try:
                    existing = sb.table("applicants").select("notes")\
                        .eq("id", student["id"]).execute().data
                    old = (existing[0].get("notes") or "") if existing else ""
                    sb.table("applicants").update({"notes": old + note})\
                        .eq("id", student["id"]).execute()
                    st.success(f"✅ {student['full_name']} allotted to {sel_block}, "
                               f"Room {room_no} ({room_type})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

    with tab_list:
        allotted = load_allotments(sb)
        if not allotted:
            st.info("No hostel allotments recorded yet.")
        else:
            st.dataframe(pd.DataFrame(allotted), use_container_width=True, hide_index=True)

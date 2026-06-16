"""Module 20 — Hostel Allotment (proper hostel_allotments table)"""
import streamlit as st
import pandas as pd
from datetime import date
from db import get_supabase
from config import MAROON, GOLD, CREAM

BLOCKS = {
    "A Block (Boys)":  {"capacity": 120, "gender": "Male"},
    "B Block (Boys)":  {"capacity": 100, "gender": "Male"},
    "C Block (Girls)": {"capacity": 150, "gender": "Female"},
    "D Block (Girls)": {"capacity": 100, "gender": "Female"},
}
ROOM_TYPES = ["Single", "Double", "Triple"]


def load_enrolled(sb, gender=None):
    try:
        q = sb.table("applicants").select(
            "id, reg_number, full_name, mobile, gender, "
            "programme_interested, department_interested, status"
        ).in_("status", ["Confirmed", "Fee Paid", "Enrolled"])
        if gender:
            q = q.eq("gender", gender)
        rows = q.order("full_name").execute().data or []
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()


def load_allotments(sb, block=None):
    try:
        q = sb.table("hostel_allotments").select(
            "*, applicants(reg_number, full_name, mobile, gender)"
        ).eq("status", "Active").order("allotment_date", desc=True)
        if block:
            q = q.eq("block_name", block)
        return q.execute().data or []
    except:
        return []


def count_allotted(sb, block_name):
    try:
        return sb.table("hostel_allotments").select("id", count="exact")\
            .eq("block_name", block_name).eq("status","Active")\
            .execute().count or 0
    except:
        return 0


def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🏠 Hostel Allotment</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Manage block and room allotment for enrolled students.
        </p>
    </div>""", unsafe_allow_html=True)

    tab_overview, tab_allot, tab_list = st.tabs(
        ["📊 Block Overview", "🛏️ Allot Room", "📋 Allotted Students"])

    # ── Tab 1: Overview ───────────────────────────────────────
    with tab_overview:
        st.subheader("Block-wise Capacity")
        rows = []
        for block, info in BLOCKS.items():
            allotted  = count_allotted(sb, block)
            available = info["capacity"] - allotted
            rows.append({
                "Block":     block,
                "Gender":    info["gender"],
                "Capacity":  info["capacity"],
                "Allotted":  allotted,
                "Available": available,
                "Fill %":    round(allotted / info["capacity"] * 100, 1),
            })
        df = pd.DataFrame(rows)

        def color_fill(val):
            if val >= 90: return "color:#E74C3C;font-weight:bold"
            if val >= 70: return "color:#F39C12;font-weight:bold"
            return "color:#27AE60"

        st.dataframe(df.style.applymap(color_fill, subset=["Fill %"]),
                     use_container_width=True, hide_index=True)

        total_cap      = sum(b["capacity"] for b in BLOCKS.values())
        total_allotted = sum(count_allotted(sb, b) for b in BLOCKS)
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Capacity", total_cap)
        k2.metric("Allotted",       total_allotted)
        k3.metric("Available",      total_cap - total_allotted)

    # ── Tab 2: Allot room ─────────────────────────────────────
    with tab_allot:
        gender_filter = st.radio("Student Gender", ["Male","Female"], horizontal=True)
        block_options = [b for b,i in BLOCKS.items() if i["gender"] == gender_filter]
        sel_block = st.selectbox("Block", block_options)
        sel_room  = st.text_input("Room Number *", placeholder="e.g. A-101")
        room_type = st.selectbox("Room Type", ROOM_TYPES)

        enrolled_df = load_enrolled(sb, gender_filter)
        if enrolled_df.empty:
            st.info(f"No {gender_filter} students in Confirmed/Enrolled status.")
        else:
            # Exclude already-allotted students
            try:
                allotted_ids = [
                    r["applicant_id"] for r in
                    sb.table("hostel_allotments").select("applicant_id")\
                      .eq("status","Active").execute().data or []
                ]
                enrolled_df = enrolled_df[~enrolled_df["id"].isin(allotted_ids)]
            except:
                pass

            if enrolled_df.empty:
                st.info("All eligible students already have hostel rooms allotted.")
            else:
                options = {
                    f"{r['reg_number']} — {r['full_name']}": r
                    for _, r in enrolled_df.iterrows()
                }
                chosen  = st.selectbox("Student *", list(options.keys()))
                student = options.get(chosen, {})

                # Check block capacity
                allotted_count = count_allotted(sb, sel_block)
                capacity       = BLOCKS[sel_block]["capacity"]
                available      = capacity - allotted_count
                st.info(f"**{sel_block}** — {available} of {capacity} rooms available")

                if st.button("🛏️ Allot Room", type="primary"):
                    if not sel_room.strip():
                        st.error("Enter a room number.")
                    elif available <= 0:
                        st.error("No rooms available in this block.")
                    else:
                        try:
                            sb.table("hostel_allotments").insert({
                                "applicant_id":   student["id"],
                                "block_name":     sel_block,
                                "room_number":    sel_room.strip(),
                                "room_type":      room_type,
                                "allotment_date": date.today().isoformat(),
                                "academic_year":  "2026-27",
                                "status":         "Active",
                            }).execute()
                            st.success(
                                f"✅ {student['full_name']} allotted to "
                                f"{sel_block}, Room {sel_room} ({room_type})")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

    # ── Tab 3: Allotted students ──────────────────────────────
    with tab_list:
        block_filter = st.selectbox("Filter by Block",
                                     ["All"] + list(BLOCKS.keys()))
        allotments   = load_allotments(sb,
                           None if block_filter == "All" else block_filter)

        if not allotments:
            st.info("No hostel allotments recorded yet.")
        else:
            rows = []
            for a in allotments:
                appl = a.get("applicants") or {}
                rows.append({
                    "Reg No":  appl.get("reg_number","") if isinstance(appl,dict) else "",
                    "Name":    appl.get("full_name","—") if isinstance(appl,dict) else "—",
                    "Mobile":  appl.get("mobile","")    if isinstance(appl,dict) else "",
                    "Gender":  appl.get("gender","")    if isinstance(appl,dict) else "",
                    "Block":   a["block_name"],
                    "Room":    a["room_number"],
                    "Type":    a["room_type"],
                    "Date":    a["allotment_date"],
                })
            df2 = pd.DataFrame(rows)
            st.markdown(f"**{len(df2)} student(s) allotted**")
            st.dataframe(df2, use_container_width=True, hide_index=True)
            csv = df2.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export CSV", csv,
                               "hostel_allotments.csv", "text/csv")

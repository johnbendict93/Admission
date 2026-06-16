"""Module 09 — Merit List"""
import streamlit as st
import pandas as pd
from config import MAROON, GOLD, CREAM
from db import get_supabase, get_lookup


def load_merit_data(sb, programme, department, category):
    try:
        q = sb.table("applicants").select(
            "reg_number, full_name, mobile, hsc_percentage, "
            "category, programme_interested, department_interested, status"
        ).eq("programme_interested", programme)\
         .eq("department_interested", department)\
         .not_.in_("status", ["Dropped", "Not Interested"])\
         .not_.is_("hsc_percentage", "null")\
         .order("hsc_percentage", desc=True)
        if category:
            q = q.eq("category", category)
        rows = q.execute().data or []
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.reset_index(drop=True)
            df.index += 1
            df.index.name = "Rank"
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()


def show():
    sb = get_supabase()
    DEPARTMENTS = get_lookup('department')
    PROGRAMMES  = get_lookup('programme')
    CATEGORIES  = get_lookup('category')

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>🏅 Merit List</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Rank applicants by HSC percentage for each programme and department.
        </p>
    </div>""", unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns(4)
    programme  = fc1.selectbox("Programme *", PROGRAMMES)
    department = fc2.selectbox("Department *", DEPARTMENTS)
    category   = fc3.selectbox("Category", ["All"] + CATEGORIES)
    min_pct    = fc4.number_input("Min HSC %", min_value=0.0,
                                   max_value=100.0, value=0.0, step=1.0)

    cat_filter = None if category == "All" else category
    df = load_merit_data(sb, programme, department, cat_filter)

    if df.empty:
        st.info(f"No applicants with HSC % data for {programme} — {department}"
                + (f" ({category})" if cat_filter else "") + ".")
        return

    if min_pct > 0:
        df = df[df["hsc_percentage"] >= min_pct]

    # ── KPIs ──────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    enrolled = len(df[df["status"] == "Enrolled"]) if not df.empty else 0
    avg_pct  = round(df["hsc_percentage"].mean(), 2) if not df.empty else 0
    top_pct  = df["hsc_percentage"].max() if not df.empty else 0

    for col, icon, val, label in [
        (k1, "👥", len(df),     "Total in List"),
        (k2, "📊", f"{avg_pct}%","Avg HSC %"),
        (k3, "🏆", f"{top_pct}%","Top HSC %"),
        (k4, "✅", enrolled,    "Enrolled"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
                <h3>{icon} {val}</h3><p>{label}</p></div>""",
                unsafe_allow_html=True)

    st.divider()

    # ── Merit table ───────────────────────────────────────────
    st.subheader(f"Merit List — {programme} / {department}"
                 + (f" / {category}" if cat_filter else ""))

    display = df[["reg_number","full_name","mobile",
                  "hsc_percentage","category","status"]].copy()
    display.columns = ["Reg No","Name","Mobile","HSC %","Category","Status"]

    # Highlight top 3
    def highlight_top(row):
        rank = row.name
        if rank == 1:   return [f"background-color:{GOLD}33"] * len(row)
        if rank == 2:   return ["background-color:#C0C0C033"] * len(row)
        if rank == 3:   return ["background-color:#CD7F3233"] * len(row)
        return [""] * len(row)

    st.dataframe(
        display.style.apply(highlight_top, axis=1),
        use_container_width=True
    )

    # ── Export ────────────────────────────────────────────────
    csv = display.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Merit List (CSV)",
        data=csv,
        file_name=f"merit_{programme}_{department}"
                  + (f"_{category}" if cat_filter else "") + ".csv",
        mime="text/csv"
    )

    # ── Cut-off analysis ──────────────────────────────────────
    with st.expander("📊 Cut-off Analysis"):
        cutoffs = [90, 85, 80, 75, 70, 60, 50]
        rows = []
        for c in cutoffs:
            count = len(df[df["hsc_percentage"] >= c])
            rows.append({"Cut-off %": f">= {c}%", "Applicants": count})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

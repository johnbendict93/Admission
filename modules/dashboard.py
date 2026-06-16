"""Module 01 — Dashboard (live Supabase data)"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db import get_supabase, get_seat_intake
from config import MAROON, GOLD, APPLICANT_STATUSES

def fetch_kpis(sb):
    try:
        total = sb.table("applicants").select("id", count="exact").execute().count or 0
    except:
        total = 0
    try:
        enrolled = sb.table("applicants").select("id", count="exact")\
            .eq("status", "Enrolled").execute().count or 0
    except:
        enrolled = 0
    try:
        pending_fu = sb.table("follow_ups").select("id", count="exact")\
            .eq("status", "Pending").execute().count or 0
    except:
        pending_fu = 0
    try:
        intake = get_seat_intake()   # {dept: capacity} from Supabase
        total_seats = sum(intake.values())
        open_seats = max(0, total_seats - enrolled)
    except:
        open_seats = 0
    return total, enrolled, pending_fu, open_seats

def fetch_pipeline(sb):
    try:
        rows = sb.table("applicants").select("status").execute().data or []
        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame()
        return df["status"].value_counts().reset_index().rename(
            columns={"index": "status", "status": "count", "count": "count"})
    except:
        return pd.DataFrame()

def fetch_dept(sb):
    try:
        rows = sb.table("applications").select("department").execute().data or []
        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame()
        return df["department"].value_counts().reset_index().rename(
            columns={"index": "department", "department": "count", "count": "count"})
    except:
        return pd.DataFrame()

def fetch_lead_source(sb):
    try:
        rows = sb.table("applicants").select("lead_source").execute().data or []
        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame()
        return df["lead_source"].value_counts().reset_index().rename(
            columns={"index": "lead_source", "lead_source": "count", "count": "count"})
    except:
        return pd.DataFrame()

def fetch_todays_followups(sb):
    try:
        from datetime import date
        today = date.today().isoformat()
        rows = sb.table("follow_ups").select(
            "title, due_date, priority, applicant_id"
        ).lte("due_date", today + "T23:59:59").eq("status", "Pending")\
         .order("due_date").limit(10).execute().data or []
        return rows
    except:
        return []


def show():
    sb = get_supabase()
    total, enrolled, pending_fu, open_seats = fetch_kpis(sb)

    # ── KPI row ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, "👤", str(total),       "Total Applicants"),
        (c2, "✅", str(enrolled),    "Enrolled"),
        (c3, "🔔", str(pending_fu),  "Pending Follow-ups"),
        (c4, "🪑", str(open_seats),  "Open Seats"),
    ]
    for col, icon, val, label in kpis:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{icon} {val}</h3>
                <p>{label}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Pipeline + Follow-ups ────────────────────────────────
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.subheader("📈 Application Pipeline")
        pipeline_df = fetch_pipeline(sb)
        if pipeline_df.empty:
            st.markdown("""
            <div class="module-placeholder">
                <p>No applicants yet — register your first walk-in to see the funnel.</p>
            </div>""", unsafe_allow_html=True)
        else:
            ordered = [s for s in APPLICANT_STATUSES if s in pipeline_df.iloc[:, 0].values]
            fig = go.Figure(go.Funnel(
                y=ordered,
                x=[pipeline_df[pipeline_df.iloc[:, 0] == s].iloc[0, 1]
                   for s in ordered if s in pipeline_df.iloc[:, 0].values],
                marker={"color": MAROON},
                textinfo="value+percent initial"
            ))
            fig.update_layout(margin=dict(t=10, b=10), height=320,
                              paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("📋 Today's Follow-ups")
        fus = fetch_todays_followups(sb)
        if not fus:
            st.info("No pending follow-ups for today.")
        else:
            for fu in fus:
                priority_color = {"Urgent": "🔴", "High": "🟠",
                                  "Normal": "🟡", "Low": "🟢"}.get(fu.get("priority", ""), "⚪")
                st.markdown(f"{priority_color} **{fu['title']}**  \n"
                            f"<small>Due: {fu['due_date'][:10]}</small>",
                            unsafe_allow_html=True)
                st.divider()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Dept enrolment + Lead source ────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🏫 Department-wise Applications")
        dept_df = fetch_dept(sb)
        if dept_df.empty:
            st.markdown("""<div class="module-placeholder">
                <p>No applications yet.</p></div>""", unsafe_allow_html=True)
        else:
            fig2 = px.bar(dept_df, x=dept_df.columns[0], y=dept_df.columns[1],
                          color_discrete_sequence=[MAROON])
            fig2.update_layout(margin=dict(t=10, b=10), height=280,
                               paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(0,0,0,0)",
                               xaxis_title="", yaxis_title="Count")
            st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.subheader("📡 Lead Source Breakdown")
        src_df = fetch_lead_source(sb)
        if src_df.empty:
            st.markdown("""<div class="module-placeholder">
                <p>No lead source data yet.</p></div>""", unsafe_allow_html=True)
        else:
            fig3 = px.pie(src_df, names=src_df.columns[0], values=src_df.columns[1],
                          color_discrete_sequence=[MAROON, GOLD, "#C0392B",
                                                   "#E8C97A", "#922B21",
                                                   "#F0D080", "#6E1414"])
            fig3.update_layout(margin=dict(t=10, b=10), height=280,
                               paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)

"""Module 05 — Lead Source Analysis"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
from config import MAROON, GOLD, CREAM, APPLICANT_STATUSES
from db import get_supabase, get_lookup


PALETTE = [MAROON, GOLD, "#C0392B", "#E8C97A", "#922B21",
           "#F0D080", "#6E1414", "#D4A843", "#A93226", "#FAD7A0"]


def load_data(sb, start_date):
    try:
        rows = sb.table("applicants").select(
            "id, lead_source, status, department_interested, created_at"
        ).gte("created_at", start_date.isoformat()).execute().data or []
        df = pd.DataFrame(rows)
        if not df.empty:
            df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
            df["month"] = df["created_at"].dt.to_period("M").astype(str)
        return df
    except Exception as e:
        st.error(f"Load error: {e}")
        return pd.DataFrame()


def empty(msg="No data yet."):
    st.markdown(f'<div class="module-placeholder"><p>{msg}</p></div>',
                unsafe_allow_html=True)


def show():
    sb = get_supabase()
    LEAD_SOURCES = get_lookup('lead_source')

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>📡 Lead Source Analysis</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Understand which channels bring the most—and best—leads.
        </p>
    </div>""", unsafe_allow_html=True)

    # ── Period picker ─────────────────────────────────────────
    pc1, _ = st.columns([2, 4])
    period = pc1.selectbox("Period", ["Last 30 days", "Last 90 days",
                                       "This Year", "All Time"])
    today = date.today()
    start = {
        "Last 30 days":  today - timedelta(days=30),
        "Last 90 days":  today - timedelta(days=90),
        "This Year":     date(today.year, 1, 1),
        "All Time":      date(2000, 1, 1),
    }[period]

    df = load_data(sb, start)

    if df.empty:
        empty("No leads recorded yet — register some walk-ins first.")
        return

    # ── KPI: leads per source ─────────────────────────────────
    src_count = df["lead_source"].value_counts()
    enrolled_by_src = df[df["status"] == "Enrolled"].groupby("lead_source").size()

    top_src   = src_count.idxmax() if not src_count.empty else "—"
    top_count = int(src_count.max()) if not src_count.empty else 0
    best_conv_src = "—"
    best_conv_rate = 0.0
    for src in src_count.index:
        rate = enrolled_by_src.get(src, 0) / src_count[src] * 100
        if rate > best_conv_rate:
            best_conv_rate = rate
            best_conv_src  = src

    k1, k2, k3, k4 = st.columns(4)
    for col, icon, val, label in [
        (k1, "📥", len(df),               "Total Leads"),
        (k2, "🏆", top_src,               "Top Source"),
        (k3, str(top_count), "👥",         "Leads from Top Source"),
        (k4, "🎯", f"{best_conv_rate:.1f}%", f"Best Conv. ({best_conv_src})"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{icon} {val}</h3><p>{label}</p>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Row 1: Pie + Bar ──────────────────────────────────────
    r1, r2 = st.columns(2)

    with r1:
        st.subheader("🥧 Volume by Source")
        vc = df["lead_source"].value_counts().reset_index()
        vc.columns = ["Source", "Count"]
        fig1 = px.pie(vc, names="Source", values="Count",
                      color_discrete_sequence=PALETTE, hole=0.35)
        fig1.update_layout(height=300, margin=dict(t=10,b=10),
                           paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, use_container_width=True)

    with r2:
        st.subheader("📊 Conversion Rate by Source (%)")
        conv_rows = []
        for src in src_count.index:
            total_src = src_count[src]
            enr = int(enrolled_by_src.get(src, 0))
            conv_rows.append({
                "Source": src,
                "Leads": int(total_src),
                "Enrolled": enr,
                "Conversion %": round(enr / total_src * 100, 1)
            })
        conv_df = pd.DataFrame(conv_rows).sort_values("Conversion %", ascending=True)
        fig2 = px.bar(conv_df, y="Source", x="Conversion %", orientation="h",
                      text="Conversion %", color_discrete_sequence=[MAROON])
        fig2.update_traces(textposition="outside")
        fig2.update_layout(height=300, margin=dict(t=10,b=10),
                           paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Monthly trend by source ───────────────────────
    st.subheader("📅 Monthly Trend by Lead Source")
    if "month" not in df.columns or df["month"].nunique() < 2:
        st.info("Need at least 2 months of data for trend chart.")
    else:
        monthly = df.groupby(["month","lead_source"]).size().reset_index(name="count")
        fig3 = px.line(monthly, x="month", y="count", color="lead_source",
                       color_discrete_sequence=PALETTE, markers=True)
        fig3.update_layout(height=320, margin=dict(t=10,b=10),
                           paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           legend_title="Lead Source",
                           xaxis_title="Month", yaxis_title="Leads")
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Summary table ─────────────────────────────────────────
    st.subheader("📋 Source Summary Table")
    st.dataframe(
        pd.DataFrame(conv_rows).sort_values("Leads", ascending=False),
        use_container_width=True, hide_index=True
    )

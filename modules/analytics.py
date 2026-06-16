"""Module 02 — Analytics & Reports (live Supabase data)"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
from db import get_supabase
from config import MAROON, GOLD, CREAM, DEPARTMENTS, PROGRAMMES, LEAD_SOURCES, APPLICANT_STATUSES


# ── Data fetchers ─────────────────────────────────────────────

def load_applicants(sb):
    try:
        rows = sb.table("applicants").select(
            "id, status, department_interested, programme_interested, "
            "lead_source, created_at, gender, category"
        ).execute().data or []
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
        df["date"] = df["created_at"].dt.date
        df["week"] = df["created_at"].dt.to_period("W").apply(lambda r: r.start_time.date())
        df["month"] = df["created_at"].dt.to_period("M").apply(lambda r: r.start_time.date())
        return df
    except Exception as e:
        st.error(f"Error loading applicants: {e}")
        return pd.DataFrame()

def load_followups(sb):
    try:
        rows = sb.table("follow_ups").select("id, status, priority, created_at").execute().data or []
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()

def load_sessions(sb):
    try:
        rows = sb.table("counseling_sessions").select(
            "id, outcome, session_type, created_at"
        ).execute().data or []
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()


# ── Helper ────────────────────────────────────────────────────

def empty_chart(msg="No data yet — register some applicants first."):
    st.markdown(f"""<div class="module-placeholder"><p>{msg}</p></div>""",
                unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────

def show():
    sb = get_supabase()

    st.markdown(f"""
    <div style='background:linear-gradient(90deg,{MAROON},{MAROON}cc);
         padding:18px 24px;border-radius:10px;margin-bottom:20px;'>
        <h2 style='color:{GOLD};margin:0;'>📊 Analytics & Reports</h2>
        <p style='color:#F5F0E8;margin:4px 0 0;font-size:0.9rem;'>
            Live insights from Supabase — all charts update in real-time.
        </p>
    </div>""", unsafe_allow_html=True)

    df = load_applicants(sb)

    # ── Date filter ───────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
    today = date.today()
    preset = col_f1.selectbox("Period", ["Last 30 days", "Last 7 days",
                                          "Last 90 days", "This Year", "All Time"])
    if preset == "Last 7 days":
        start_d = today - timedelta(days=7)
    elif preset == "Last 30 days":
        start_d = today - timedelta(days=30)
    elif preset == "Last 90 days":
        start_d = today - timedelta(days=90)
    elif preset == "This Year":
        start_d = date(today.year, 1, 1)
    else:
        start_d = date(2000, 1, 1)

    dept_filter = col_f2.multiselect("Department", DEPARTMENTS)

    if not df.empty:
        mask = df["date"] >= start_d
        if dept_filter:
            mask &= df["department_interested"].isin(dept_filter)
        fdf = df[mask].copy()
    else:
        fdf = df.copy()

    # ── KPI strip ─────────────────────────────────────────────
    total      = len(fdf)
    enrolled   = len(fdf[fdf["status"] == "Enrolled"]) if not fdf.empty else 0
    confirmed  = len(fdf[fdf["status"] == "Confirmed"]) if not fdf.empty else 0
    conversion = round((enrolled / total * 100), 1) if total else 0

    k1, k2, k3, k4 = st.columns(4)
    for col, icon, val, label in [
        (k1, "👤", total,           "Total in Period"),
        (k2, "✅", enrolled,        "Enrolled"),
        (k3, "🤝", confirmed,       "Confirmed"),
        (k4, "📈", f"{conversion}%","Enrolment Rate"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{icon} {val}</h3><p>{label}</p>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Row 1: Daily trend + Status funnel ────────────────────
    r1a, r1b = st.columns([3, 2])

    with r1a:
        st.subheader("📅 Daily Registrations Trend")
        if fdf.empty:
            empty_chart()
        else:
            trend = fdf.groupby("date").size().reset_index(name="count")
            trend["date"] = pd.to_datetime(trend["date"])
            fig = px.area(trend, x="date", y="count",
                          color_discrete_sequence=[MAROON])
            fig.update_layout(height=280, margin=dict(t=10,b=10),
                              paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              xaxis_title="", yaxis_title="Walk-ins")
            fig.update_traces(fill="tozeroy", line_color=MAROON,
                              fillcolor=f"rgba(139,26,26,0.15)")
            st.plotly_chart(fig, use_container_width=True)

    with r1b:
        st.subheader("🔽 Status Funnel")
        if fdf.empty:
            empty_chart()
        else:
            counts = fdf["status"].value_counts()
            ordered = [s for s in APPLICANT_STATUSES if s in counts.index]
            fig2 = go.Figure(go.Funnel(
                y=ordered,
                x=[counts[s] for s in ordered],
                marker={"color": MAROON},
                textinfo="value+percent initial"
            ))
            fig2.update_layout(height=280, margin=dict(t=10,b=10),
                               paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Row 2: Dept bar + Programme pie ───────────────────────
    r2a, r2b = st.columns(2)

    with r2a:
        st.subheader("🏫 Department-wise Count")
        if fdf.empty:
            empty_chart()
        else:
            dept_c = fdf["department_interested"].value_counts().reset_index()
            dept_c.columns = ["Department", "Count"]
            fig3 = px.bar(dept_c, x="Department", y="Count",
                          color_discrete_sequence=[MAROON],
                          text="Count")
            fig3.update_traces(textposition="outside")
            fig3.update_layout(height=300, margin=dict(t=10,b=10),
                               paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)

    with r2b:
        st.subheader("🎓 Programme Distribution")
        if fdf.empty:
            empty_chart()
        else:
            prog_c = fdf["programme_interested"].value_counts().reset_index()
            prog_c.columns = ["Programme", "Count"]
            fig4 = px.pie(prog_c, names="Programme", values="Count",
                          color_discrete_sequence=[MAROON, GOLD, "#C0392B",
                                                   "#E8C97A", "#922B21", "#F0D080"])
            fig4.update_layout(height=300, margin=dict(t=10,b=10),
                               paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # ── Row 3: Lead source + Gender ───────────────────────────
    r3a, r3b = st.columns(2)

    with r3a:
        st.subheader("📡 Lead Source Breakdown")
        if fdf.empty:
            empty_chart()
        else:
            src_c = fdf["lead_source"].value_counts().reset_index()
            src_c.columns = ["Source", "Count"]
            fig5 = px.bar(src_c, y="Source", x="Count", orientation="h",
                          color_discrete_sequence=[GOLD], text="Count")
            fig5.update_traces(textposition="outside", marker_color=MAROON)
            fig5.update_layout(height=300, margin=dict(t=10,b=10),
                               paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(0,0,0,0)",
                               yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig5, use_container_width=True)

    with r3b:
        st.subheader("⚧ Gender Split")
        if fdf.empty or "gender" not in fdf.columns:
            empty_chart()
        else:
            gen_c = fdf["gender"].dropna().value_counts().reset_index()
            gen_c.columns = ["Gender", "Count"]
            if gen_c.empty:
                empty_chart("No gender data recorded yet.")
            else:
                fig6 = px.pie(gen_c, names="Gender", values="Count",
                              color_discrete_sequence=[MAROON, GOLD, "#888"])
                fig6.update_layout(height=300, margin=dict(t=10,b=10),
                                   paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig6, use_container_width=True)

    st.divider()

    # ── Raw data export ───────────────────────────────────────
    with st.expander("⬇️ Export Raw Data (CSV)"):
        if fdf.empty:
            st.info("No data to export for the selected period.")
        else:
            csv = fdf.drop(columns=["week", "month", "date"], errors="ignore")\
                     .to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"dce_analytics_{today}.csv",
                mime="text/csv"
            )
            st.dataframe(fdf.drop(columns=["week","month","date"], errors="ignore"),
                         use_container_width=True, hide_index=True)

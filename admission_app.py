"""
DCE Admission CRM — Main Entry Point
=====================================
Run:  streamlit run admission_app.py
Repo: https://github.com/johnbendict93/Admission
"""

import importlib
import streamlit as st
from config import (
    APP_TITLE, COLLEGE_NAME, COLLEGE_SHORT,
    MAROON, GOLD, CREAM, MODULES,
)

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — DCE Maroon & Gold ───────────────────────────
st.markdown(f"""
<style>
/* Sidebar background */
[data-testid="stSidebar"] {{
    background-color: {MAROON};
}}
[data-testid="stSidebar"] * {{
    color: #FFFFFF !important;
}}

/* Sidebar radio buttons — module navigation */
[data-testid="stSidebar"] .stRadio label {{
    color: #F5E8C8 !important;
    font-size: 0.88rem;
    padding: 2px 0;
}}
[data-testid="stSidebar"] .stRadio div[data-checked="true"] label {{
    color: {GOLD} !important;
    font-weight: 700;
}}

/* Section headings in sidebar */
.sidebar-section {{
    color: {GOLD};
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 14px 0 4px 0;
    padding-left: 4px;
    border-left: 3px solid {GOLD};
    padding-left: 8px;
}}

/* Top header bar */
.crm-header {{
    background: linear-gradient(135deg, {MAROON} 0%, #5C0F0F 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}}
.crm-header h1 {{
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
    color: white;
}}
.crm-header span {{
    color: {GOLD};
    font-size: 0.9rem;
}}

/* Metric cards */
.metric-card {{
    background: white;
    border-left: 5px solid {MAROON};
    border-radius: 6px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}
.metric-card h3 {{
    margin: 0;
    font-size: 2rem;
    color: {MAROON};
}}
.metric-card p {{
    margin: 0.2rem 0 0 0;
    color: #666;
    font-size: 0.85rem;
}}

/* Gold accent buttons */
.stButton > button {{
    background-color: {MAROON};
    color: white;
    border: 2px solid {GOLD};
    border-radius: 6px;
    font-weight: 600;
}}
.stButton > button:hover {{
    background-color: {GOLD};
    color: {MAROON};
    border-color: {MAROON};
}}

/* Section divider */
.section-divider {{
    border: 0;
    border-top: 2px solid {GOLD};
    margin: 1rem 0;
}}

/* Module placeholder card */
.module-placeholder {{
    background: {CREAM};
    border: 2px dashed {GOLD};
    border-radius: 10px;
    padding: 3rem 2rem;
    text-align: center;
    color: {MAROON};
}}
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ────────────────────────────────────
if "active_module" not in st.session_state:
    st.session_state.active_module = "dashboard"
if "user_role" not in st.session_state:
    st.session_state.user_role = "admin"      # TODO: wire to Supabase auth


# ── Sidebar — logo + navigation ───────────────────────────────
with st.sidebar:
    # College logo / wordmark
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
        <div style="font-size:2.2rem;">🎓</div>
        <div style="color:{GOLD}; font-weight:700; font-size:1.1rem;">{COLLEGE_SHORT}</div>
        <div style="color:#FFE4B5; font-size:0.7rem; margin-top:2px;">Admission CRM</div>
    </div>
    <hr style="border-color:{GOLD}33; margin:8px 0 4px 0;">
    """, unsafe_allow_html=True)

    # Build section → module map
    sections: dict[str, list] = {}
    for name, icon, key, section in MODULES:
        sections.setdefault(section, []).append((name, icon, key))

    # Render each section + radio group
    for section, items in sections.items():
        st.markdown(f'<div class="sidebar-section">{section}</div>', unsafe_allow_html=True)
        for name, icon, key in items:
            label = f"{icon} {name}"
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="secondary" if st.session_state.active_module != key else "primary",
            ):
                st.session_state.active_module = key
                st.rerun()

    # Footer
    st.markdown(f"""
    <hr style="border-color:{GOLD}33; margin-top:1rem;">
    <div style="text-align:center; font-size:0.65rem; color:#FFE4B5; padding-bottom:0.5rem;">
        {COLLEGE_NAME}<br>Academic Year 2026–27
    </div>
    """, unsafe_allow_html=True)


# ── Header bar ────────────────────────────────────────────────
# Find current module display name
current_name = next(
    (name for name, icon, key, _ in MODULES if key == st.session_state.active_module),
    "Dashboard",
)
current_icon = next(
    (icon for name, icon, key, _ in MODULES if key == st.session_state.active_module),
    "🏠",
)

st.markdown(f"""
<div class="crm-header">
    <h1>{current_icon} {current_name}</h1>
    <span>👤 {st.session_state.get("user_name", "Admin")} &nbsp;|&nbsp; 🗓️ 2026–27</span>
</div>
""", unsafe_allow_html=True)


# ── Module loader ─────────────────────────────────────────────
active = st.session_state.active_module
try:
    mod = importlib.import_module(f"modules.{active}")
    mod.show()
except ModuleNotFoundError:
    st.info(f"Module `modules/{active}.py` not found — create it and add a `show()` function.")
except Exception as e:
    st.error(f"Error loading module **{active}**: {e}")
    st.exception(e)

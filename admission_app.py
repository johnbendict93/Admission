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
from db import get_college_name, get_academic_year

# ── Page config ──────────────────────────────────────────────
_logged_in_check = "auth_user" in st.session_state
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded" if _logged_in_check else "collapsed",
)

# ── Global CSS ───────────────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="stSidebar"] {{
    background-color: {MAROON};
}}
[data-testid="stSidebar"] * {{
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] .stRadio label {{
    color: #F5E8C8 !important;
    font-size: 0.88rem;
}}
.sidebar-section {{
    color: {GOLD};
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 14px 0 4px 0;
    border-left: 3px solid {GOLD};
    padding-left: 8px;
}}
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
.crm-header h1 {{ margin:0; font-size:1.6rem; font-weight:700; color:white; }}
.crm-header span {{ color:{GOLD}; font-size:0.9rem; }}
.metric-card {{
    background: white;
    border-left: 5px solid {MAROON};
    border-radius: 6px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}
.metric-card h3 {{ margin:0; font-size:2rem; color:{MAROON}; }}
.metric-card p  {{ margin:0.2rem 0 0 0; color:#666; font-size:0.85rem; }}
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
.section-divider {{ border:0; border-top:2px solid {GOLD}; margin:1rem 0; }}
.module-placeholder {{
    background: {CREAM};
    border: 2px dashed {GOLD};
    border-radius: 10px;
    padding: 3rem 2rem;
    text-align: center;
    color: {MAROON};
}}
/* Login page */
.login-card {{
    max-width: 420px;
    margin: 6vh auto;
    background: white;
    border-radius: 16px;
    padding: 2.5rem 2rem;
    box-shadow: 0 8px 32px rgba(139,26,26,0.15);
    border-top: 6px solid {MAROON};
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════════

def get_sb():
    """Return Supabase client (cached)."""
    from db import get_supabase
    return get_supabase()


def do_login(email: str, password: str):
    """Attempt Supabase email+password sign-in."""
    sb = get_sb()
    try:
        resp = sb.auth.sign_in_with_password({"email": email, "password": password})
        if resp.user:
            st.session_state["auth_user"]  = resp.user
            st.session_state["auth_token"] = resp.session.access_token
            # Pull display name from users table
            row = sb.table("users").select("full_name, role")\
                    .eq("email", email).execute().data
            if row:
                st.session_state["user_name"] = row[0]["full_name"]
                st.session_state["user_role"] = row[0]["role"]
            else:
                st.session_state["user_name"] = resp.user.email
                st.session_state["user_role"] = "admin"
            return True, None
        return False, "Invalid credentials."
    except Exception as e:
        msg = str(e)
        if "Invalid login credentials" in msg:
            return False, "Wrong email or password."
        return False, msg


def do_logout():
    for key in ["auth_user","auth_token","user_name","user_role","active_module"]:
        st.session_state.pop(key, None)
    try:
        get_sb().auth.sign_out()
    except:
        pass
    st.rerun()


def is_logged_in() -> bool:
    return "auth_user" in st.session_state


# ═══════════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════════

def show_login():
    st.markdown(f"""
    <div class="login-card">
        <div style="text-align:center; margin-bottom:1.5rem;">
            <div style="font-size:3rem;">🎓</div>
            <h2 style="color:{MAROON}; margin:0.3rem 0 0.1rem 0;">DCE Admission CRM</h2>
            <p style="color:#888; font-size:0.85rem; margin:0;">{get_college_name()}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email    = st.text_input("Email", placeholder="you@dce.ac.in")
        password = st.text_input("Password", type="password")
        submit   = st.form_submit_button("Sign In", use_container_width=True, type="primary")

    if submit:
        if not email.strip() or not password.strip():
            st.error("Enter email and password.")
        else:
            with st.spinner("Signing in…"):
                ok, err = do_login(email.strip(), password.strip())
            if ok:
                st.session_state.setdefault("active_module", "dashboard")
                st.rerun()
            else:
                st.error(f"Login failed: {err}")

    st.markdown("""
    <p style="text-align:center; font-size:0.8rem; color:#aaa; margin-top:1rem;">
        First time? Create your account via Supabase Auth → Settings &amp; Admin.
    </p>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN APP (authenticated)
# ═══════════════════════════════════════════════════════════════

def show_app():
    # Session defaults
    st.session_state.setdefault("active_module", "dashboard")

    # ── Sidebar ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:1rem 0 0.5rem 0;">
            <div style="font-size:2.2rem;">🎓</div>
            <div style="color:{GOLD}; font-weight:700; font-size:1.1rem;">{COLLEGE_SHORT}</div>
            <div style="color:#FFE4B5; font-size:0.7rem; margin-top:2px;">Admission CRM</div>
        </div>
        <hr style="border-color:{GOLD}33; margin:8px 0 4px 0;">
        """, unsafe_allow_html=True)

        # User info
        uname = st.session_state.get("user_name","User")
        urole = st.session_state.get("user_role","—")
        st.markdown(f"""
        <div style="text-align:center; padding:4px 0 8px 0;">
            <div style="color:{GOLD}; font-size:0.8rem;">👤 {uname}</div>
            <div style="color:#FFE4B5; font-size:0.7rem;">{urole.upper()}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        sections: dict[str, list] = {}
        for name, icon, key, section in MODULES:
            sections.setdefault(section, []).append((name, icon, key))

        for section, items in sections.items():
            st.markdown(f'<div class="sidebar-section">{section}</div>',
                        unsafe_allow_html=True)
            for name, icon, key in items:
                is_active = st.session_state.active_module == key
                if st.button(
                    f"{icon} {name}",
                    key=f"nav_{key}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state.active_module = key
                    st.rerun()

        st.markdown(f'<hr style="border-color:{GOLD}33; margin-top:1rem;">',
                    unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            do_logout()

        st.markdown(f"""
        <div style="text-align:center; font-size:0.65rem; color:#FFE4B5; padding-bottom:0.5rem;">
            {get_college_name()}<br>Academic Year {get_academic_year()}
        </div>""", unsafe_allow_html=True)

    # ── Header bar ────────────────────────────────────────────
    active = st.session_state.active_module
    current_name = next(
        (n for n, i, k, _ in MODULES if k == active), "Dashboard")
    current_icon = next(
        (i for n, i, k, _ in MODULES if k == active), "🏠")

    st.markdown(f"""
    <div class="crm-header">
        <h1>{current_icon} {current_name}</h1>
        <span>👤 {uname} &nbsp;|&nbsp; 🗓️ {get_academic_year()}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Module loader ─────────────────────────────────────────
    try:
        mod = importlib.import_module(f"modules.{active}")
        mod.show()
    except ModuleNotFoundError:
        st.info(f"Module `modules/{active}.py` not found.")
    except Exception as e:
        st.error(f"Error in module **{active}**: {e}")
        st.exception(e)


# ═══════════════════════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════════════


if is_logged_in():
    show_app()
else:
    show_login()
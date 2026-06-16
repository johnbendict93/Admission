"""db.py — Supabase client + cached dynamic config loaders"""
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


# ── Lookup values (departments, programmes, categories, etc.) ─

@st.cache_data(ttl=300)
def get_lookup(lookup_type: str) -> list[str]:
    """Return ordered list of active lookup values by type."""
    try:
        rows = get_supabase().table("lookup_values").select("value")\
            .eq("type", lookup_type).eq("is_active", True)\
            .order("sort_order").execute().data or []
        return [r["value"] for r in rows]
    except Exception as e:
        st.warning(f"Could not load lookup '{lookup_type}': {e}")
        return []


@st.cache_data(ttl=300)
def get_setting(category: str, key: str, default: str = "") -> str:
    """Return a single setting value."""
    try:
        rows = get_supabase().table("settings").select("value")\
            .eq("category", category).eq("key", key)\
            .eq("is_active", True).execute().data
        return rows[0]["value"] if rows else default
    except:
        return default


@st.cache_data(ttl=300)
def get_settings_by_category(category: str) -> dict:
    """Return all settings for a category as {key: value}."""
    try:
        rows = get_supabase().table("settings").select("key, value")\
            .eq("category", category).eq("is_active", True).execute().data or []
        return {r["key"]: r["value"] for r in rows}
    except:
        return {}


@st.cache_data(ttl=300)
def get_fee_structure() -> dict:
    """Return {(programme, dept): {component: amount}} from settings table."""
    rows = get_supabase().table("settings").select("key, value")\
        .eq("category", "fee").execute().data or []
    result: dict = {}
    for r in rows:
        parts = r["key"].split("|")
        if len(parts) == 3:
            prog, dept, component = parts
            result.setdefault((prog, dept), {})[component] = int(r["value"])
    return result


@st.cache_data(ttl=300)
def get_seat_intake() -> dict:
    """Return {dept: capacity} from settings table."""
    rows = get_supabase().table("settings").select("key, value")\
        .eq("category", "seat_intake").execute().data or []
    return {r["key"]: int(r["value"]) for r in rows}


@st.cache_data(ttl=300)
def get_hostel_blocks() -> dict:
    """Return {block_name: {capacity: int, gender: str}} from settings table."""
    rows = get_supabase().table("settings").select("key, value")\
        .eq("category", "hostel_block").execute().data or []
    result: dict = {}
    for r in rows:
        parts = r["key"].split("|")
        if len(parts) == 2:
            block, attr = parts
            result.setdefault(block, {})[attr] = r["value"]
    for block in result:
        if "capacity" in result[block]:
            result[block]["capacity"] = int(result[block]["capacity"])
    return result


@st.cache_data(ttl=300)
def get_document_types() -> list[str]:
    """Return ordered list of active document type names."""
    try:
        rows = get_supabase().table("document_types").select("name")\
            .eq("is_active", True).order("sort_order").execute().data or []
        return [r["name"] for r in rows]
    except:
        return []


@st.cache_data(ttl=300)
def get_applicant_statuses() -> list[str]:
    """Return ordered applicant status workflow from Supabase.
    Falls back to config list if Supabase returns nothing."""
    from config import APPLICANT_STATUSES as _DEFAULT
    try:
        rows = get_supabase().table("lookup_values").select("value") \
            .eq("type", "applicant_status").eq("is_active", True) \
            .order("sort_order").execute().data or []
        result = [r["value"] for r in rows]
        return result if result else _DEFAULT
    except:
        return _DEFAULT


@st.cache_data(ttl=300)
def get_college_name() -> str:
    """Return college name from Supabase general settings, fallback to config."""
    from config import COLLEGE_NAME as _DEFAULT
    return get_setting("general", "college_name", _DEFAULT)


@st.cache_data(ttl=300)
def get_academic_year() -> str:
    """Return academic year from Supabase general settings, fallback to config."""
    from config import ACADEMIC_YEAR as _DEFAULT
    return get_setting("general", "academic_year", _DEFAULT)


def clear_config_cache():
    """Call after updating settings to refresh cached values."""
    get_lookup.clear()
    get_setting.clear()
    get_settings_by_category.clear()
    get_fee_structure.clear()
    get_seat_intake.clear()
    get_hostel_blocks.clear()
    get_document_types.clear()
    get_applicant_statuses.clear()
    get_college_name.clear()
    get_academic_year.clear()

# db.py — Supabase client singleton

import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    """Return a cached Supabase client using secrets from .streamlit/secrets.toml"""
    url  = st.secrets["supabase"]["url"]
    key  = st.secrets["supabase"]["key"]
    return create_client(url, key)

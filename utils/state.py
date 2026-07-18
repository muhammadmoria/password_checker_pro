"""Streamlit session state initialization."""
import streamlit as st


def init_session_state():
    """Initialize default session state values."""
    defaults = {
        "authenticated": False,
        "current_user": None,
        "vault_crypto": None,
        "vault_unlocked": False,
        "page": "Dashboard",
        "last_analysis": None,
        "sidebar_collapsed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
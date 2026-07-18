"""Utility helper functions."""
import streamlit as st


def mask_password(password: str) -> str:
    if len(password) <= 2:
        return "*" * len(password)
    return password[0] + "*" * (len(password) - 2) + password[-1]


def get_session_user_id() -> int | None:
    user = st.session_state.get("current_user")
    if user:
        return user.get("id")
    return None


def set_session_user(user_dict: dict):
    st.session_state["current_user"] = user_dict
    st.session_state["authenticated"] = True


def clear_session():
    keys_to_remove = [k for k in st.session_state.keys() if k not in ("page",)]
    for key in keys_to_remove:
        del st.session_state[key]
    st.session_state["authenticated"] = False


def format_number(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
"""Sidebar navigation component."""
import streamlit as st

def render_sidebar() -> str:
    """Render the sidebar navigation and return the selected page name."""
    with st.sidebar:
        # Brand Header
        st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-logo">🔐</div>
            <div class="sidebar-title">Password Checker</div>
            <div class="sidebar-subtitle">AI Pro</div>
        </div>
        """, unsafe_allow_html=True)

        user = st.session_state.get("current_user")
        is_admin = user and user.get("is_admin", False)
        current_page = st.session_state.get("page", "Dashboard")

        # Navigation Sections
        st.markdown('<div class="nav-section-label">Main</div>', unsafe_allow_html=True)
        _render_nav_button("Dashboard", "📊", current_page)
        _render_nav_button("Analyzer", "🔍", current_page)
        _render_nav_button("Leak Checker", "🛡️", current_page)

        st.markdown('<div class="nav-section-label">Tools</div>', unsafe_allow_html=True)
        _render_nav_button("Generator", "🔐", current_page)
        _render_nav_button("Vault", "🗝️", current_page)
        _render_nav_button("History", "📜", current_page)

        st.markdown('<div class="nav-section-label">System</div>', unsafe_allow_html=True)
        _render_nav_button("Settings", "⚙️", current_page)
        if is_admin:
            _render_nav_button("Admin", "👑", current_page)

        st.markdown("---")

        # User Profile Card
        if user:
            role = "Administrator" if user.get("is_admin") else "Standard User"
            role_color = "#bd00ff" if is_admin else "#00d4ff"
            
            st.markdown(f"""
            <div class="sidebar-user" style="border-left: 3px solid {role_color};">
                <div class="user-avatar" style="border-color: {role_color}; color: {role_color};">
                    {'👑' if is_admin else '👤'}
                </div>
                <div>
                    <div class="user-name">{user.get('username', 'Unknown')}</div>
                    <div class="user-role" style="color: {role_color};">{role}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
                from utils.helpers import clear_session
                clear_session()
                st.rerun()

        # System Status
        st.markdown("""
        <div class="sidebar-footer">
            <div style="display:flex; align-items:center; justify-content:center; gap:6px; margin-bottom: 8px;">
                <span style="width:8px; height:8px; background:#10b981; border-radius:50%; box-shadow: 0 0 8px #10b981; display:inline-block; animation: pulse 2s infinite;"></span>
                <span style="font-size:0.75rem; color:#10b981; font-weight:600;">System Operational</span>
            </div>
            <div>v1.0.0 · Enterprise Edition</div>
            <div style="margin-top:4px;font-size:0.7rem;opacity:0.5;">Secure by Design</div>
        </div>
        """, unsafe_allow_html=True)

    return current_page

def _render_nav_button(page_name: str, icon: str, current_page: str):
    """Helper to render a navigation button."""
    if st.button(f"{icon}  {page_name}", key=f"nav_{page_name}", use_container_width=True):
        st.session_state["page"] = page_name
        st.rerun()
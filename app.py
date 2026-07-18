"""
Password Strength & Leak Checker AI Pro
=======================================
Enterprise-grade password security analysis, breach checking, and vault management.

Run with:
    streamlit run app.py
"""
import logging
import streamlit as st
from config import settings

# ==========================================
# Config & Initialization
# ==========================================

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Core imports
from database.connection import init_database
from database.init_db import ensure_admin_user
from utils.state import init_session_state
from components.ui import load_css, render_background, info_banner, glass_card
from components.sidebar import render_sidebar
from services.auth_service import AuthService

# Page imports
from pages.dashboard import render_dashboard
from pages.analyzer import render_analyzer
from pages.leak_checker import render_leak_checker
from pages.generator import render_generator
from pages.vault import render_vault
from pages.history import render_history
from pages.settings import render_settings
from pages.admin import render_admin

PAGE_MAP = {
    "Dashboard": render_dashboard,
    "Analyzer": render_analyzer,
    "Leak Checker": render_leak_checker,
    "Generator": render_generator,
    "Vault": render_vault,
    "History": render_history,
    "Settings": render_settings,
    "Admin": render_admin,
}

def init_app():
    """Initialize the application: database, session state, and styles."""
    try:
        init_database()
        ensure_admin_user()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error("Database initialization error: %s", e)
        st.error("Fatal Error: Could not initialize the database. Please check your configuration.")

    init_session_state()
    load_css()
    render_background()


# ==========================================
# Authentication Views
# ==========================================

def render_auth_page():
    """Render the premium login/register page."""
    # Inject specific auth page styling to center everything perfectly
    st.markdown("""
    <style>
        .main > div {
            padding-top: 4rem !important;
        }
        .auth-wrapper {
            max-width: 480px;
            margin: 0 auto;
            animation: fadeIn 0.8s ease-out;
        }
        .auth-brand {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        .auth-brand-icon {
            font-size: 4.5rem;
            line-height: 1;
            margin-bottom: 1rem;
            filter: drop-shadow(0 0 25px rgba(0, 212, 255, 0.6));
            animation: pulse 3s infinite ease-in-out;
        }
        .auth-brand-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -1.5px;
            color: #e2e8f0;
            margin-bottom: 0.5rem;
        }
        .auth-brand-subtitle {
            font-size: 0.95rem;
            color: #64748b;
            font-weight: 500;
        }
        .auth-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
        }
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .auth-header h2 {
            font-size: 1.5rem;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 0.25rem;
        }
        .auth-header p {
            font-size: 0.9rem;
            color: #94a3b8;
        }
        .auth-footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            color: #64748b;
            font-size: 0.8rem;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); filter: drop-shadow(0 0 25px rgba(0, 212, 255, 0.6)); }
            50% { transform: scale(1.05); filter: drop-shadow(0 0 35px rgba(0, 212, 255, 0.9)); }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
    
    # Branding
    st.markdown("""
    <div class="auth-brand">
        <div class="auth-brand-icon">🔐</div>
        <div class="auth-brand-title">Password Checker <span style="color:#bd00ff;">AI Pro</span></div>
        <div class="auth-brand-subtitle">Next-Generation Security Suite</div>
    </div>
    """, unsafe_allow_html=True)

    # Auth Card
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "✨ Create Account"])

    with tab1:
        _render_login()
    with tab2:
        _render_register()

    st.markdown("""
    <div class="auth-footer">
        Protected by Advanced Encryption Standards (AES-256)<br>
        <span style="opacity: 0.6;">v1.0.0 · Enterprise Edition</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_login():
    st.markdown('<div class="auth-header"><h2>Welcome Back</h2><p>Access your secure dashboard</p></div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pw")
        
        submit = st.form_submit_button("🚀 Sign In Securely", use_container_width=True, type="primary")
        
        if submit:
            if not username or not password:
                info_banner("Please enter both username and password.", "warning")
                return

            with st.spinner("Verifying credentials..."):
                auth = AuthService()
                ok, msg, user = auth.login(username, password)
                
            if ok:
                from utils.helpers import set_session_user
                set_session_user(user.to_dict())
                st.rerun()
            else:
                info_banner(msg, "error")

    st.markdown("""
    <div style="text-align:center;margin-top:1.5rem;color:#64748b;font-size:0.85rem;">
        💡 Default Admin: <code style="color:#00d4ff; background: rgba(0,212,255,0.1); padding: 2px 6px; border-radius: 4px;">admin</code> / <code style="color:#00d4ff; background: rgba(0,212,255,0.1); padding: 2px 6px; border-radius: 4px;">ChangeMeImmediately123!</code>
    </div>
    """, unsafe_allow_html=True)


def _render_register():
    st.markdown('<div class="auth-header"><h2>Create Account</h2><p>Join to secure your digital life</p></div>', unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Choose a username (min 3 chars)", key="reg_user")
        password = st.text_input("Password", type="password", placeholder="Choose a password (min 8 chars)", key="reg_pw")
        confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="reg_confirm")
        
        submit = st.form_submit_button("📝 Create Secure Account", use_container_width=True, type="primary")
        
        if submit:
            if not username or not password:
                info_banner("All fields are required.", "warning")
                return
            if password != confirm:
                info_banner("Passwords do not match.", "error")
                return

            with st.spinner("Creating your secure vault..."):
                auth = AuthService()
                ok, msg, user = auth.register(username, password, is_admin=False)
                
            if ok:
                info_banner("Account created successfully! Please sign in.", "success")
            else:
                info_banner(msg, "error")


# ==========================================
# Global UI Elements
# ==========================================

def render_top_bar(selected_page: str):
    """Render a premium top header for the authenticated application."""
    user = st.session_state.get("current_user", {})
    username = user.get("username", "Guest")
    role = "Administrator" if user.get("is_admin") else "Standard User"
    
    st.markdown(f"""
    <div class="glass-card" style="display:flex; justify-content:space-between; align-items:center; padding: 1rem 1.5rem; margin-bottom: 1.5rem; border-radius: 12px;">
        <div style="display:flex; align-items:center; gap: 0.75rem;">
            <span style="font-size: 1.5rem;">📋</span>
            <div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #e2e8f0;">{selected_page}</div>
                <div style="font-size: 0.75rem; color: #64748b;">Secure Session Active</div>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap: 1rem;">
            <div style="text-align:right;">
                <div style="font-size: 0.9rem; font-weight: 600; color: #00d4ff;">{username}</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">{role}</div>
            </div>
            <div style="width: 40px; height: 40px; background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 50%; display:flex; align-items:center; justify-content:center; font-size: 1.2rem;">
                👤
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render a premium footer."""
    st.markdown("""
    <div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.05); text-align: center; color: #64748b; font-size: 0.8rem;">
        <div>Password Strength & Leak Checker AI Pro · Enterprise Edition</div>
        <div style="margin-top: 0.25rem; opacity: 0.7;">Built with Streamlit, SQLAlchemy, and Advanced Cryptography · &copy; 2024</div>
    </div>
    """, unsafe_allow_html=True)


def render_error_page(error: Exception):
    """Render a beautiful error page when a module fails to load."""
    st.markdown("""
    <div style="text-align:center; padding: 3rem 1rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">⚠️</div>
        <h2 style="color: #ef4444; font-weight: 700; margin-bottom: 0.5rem;">System Error</h2>
        <p style="color: #94a3b8; margin-bottom: 2rem;">An unexpected error occurred while loading this module.</p>
    </div>
    """, unsafe_allow_html=True)
    
    glass_card(f"""
    <div style="font-family: monospace; font-size: 0.85rem; color: #f87171; background: rgba(239, 68, 68, 0.05); padding: 1rem; border-radius: 8px; border: 1px solid rgba(239, 68, 68, 0.2);">
        <div style="font-weight: bold; margin-bottom: 0.5rem; color: #fca5a5;">Error Details:</div>
        {str(error)}
    </div>
    """)
    
    st.info("Please check the console logs for a full traceback or try restarting the application.")


# ==========================================
# Main Router
# ==========================================

def main():
    """Main application router."""
    st.set_page_config(
        page_title="Password Checker AI Pro",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_app()

    # Authentication Gate
    if not st.session_state.get("authenticated"):
        render_auth_page()
        return

    # Authenticated App
    selected_page = render_sidebar()
    render_top_bar(selected_page)

    # Page Renderer with Error Boundary
    page_renderer = PAGE_MAP.get(selected_page, render_dashboard)
    try:
        page_renderer()
    except Exception as e:
        logger.error("Error rendering page '%s': %s", selected_page, e, exc_info=True)
        render_error_page(e)

    render_footer()


if __name__ == "__main__":
    main()
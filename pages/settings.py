"""Settings page."""
import streamlit as st
from components.ui import section_header, info_banner
from services.auth_service import AuthService
from security.validation import validate_password_length
from utils.helpers import get_session_user_id


def render_settings():
    st.markdown('<div class="neon-text-blue" style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Manage your account and preferences</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔐 Account", "🎨 Preferences", "ℹ️ About"])

    with tab1:
        _render_account_settings()
    with tab2:
        _render_preferences()
    with tab3:
        _render_about()


def _render_account_settings():
    user = st.session_state.get("current_user")
    if not user:
        st.error("Not authenticated.")
        return

    section_header("Account Information", "👤")
    st.markdown(f"""
    <div class="glass-card">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
            <div><strong style="color:#94a3b8;">Username:</strong> {user.get('username')}</div>
            <div><strong style="color:#94a3b8;">Role:</strong> {'Administrator' if user.get('is_admin') else 'User'}</div>
            <div><strong style="color:#94a3b8;">User ID:</strong> {user.get('id')}</div>
            <div><strong style="color:#94a3b8;">Status:</strong> {'Active' if user.get('is_active') else 'Inactive'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    section_header("Change Password", "🔑")

    old_pw = st.text_input("Current Password", type="password", key="set_old_pw")
    new_pw = st.text_input("New Password", type="password", key="set_new_pw")
    confirm_pw = st.text_input("Confirm New Password", type="password", key="set_confirm_pw")

    if st.button("🔄 Change Password", use_container_width=True, type="primary"):
        if not old_pw or not new_pw or not confirm_pw:
            st.error("All fields are required.")
            return
        if new_pw != confirm_pw:
            st.error("New passwords do not match.")
            return

        valid, msg = validate_password_length(new_pw, min_length=8)
        if not valid:
            st.error(msg)
            return

        auth = AuthService()
        ok, msg = auth.change_password(user["id"], old_pw, new_pw)
        if ok:
            st.success(msg)
            st.session_state["vault_unlocked"] = False
            st.session_state["vault_crypto"] = None
        else:
            st.error(msg)

    st.markdown("---")
    section_header("Vault Security", "🔒")
    if st.session_state.get("vault_unlocked"):
        st.success("Vault is currently unlocked.")
        if st.button("🔒 Lock Vault Now", use_container_width=True):
            st.session_state["vault_unlocked"] = False
            st.session_state["vault_crypto"] = None
            st.rerun()
    else:
        st.info("Vault is currently locked.")


def _render_preferences():
    section_header("Display Preferences", "🎨")

    st.markdown("**Note:** Theme is configured via `.streamlit/config.toml`.")

    st.markdown("""
    <div class="glass-card">
        <div style="color:#94a3b8;font-size:0.9rem;">
            <strong>Current Theme:</strong> Dark (Neon Blue/Purple)<br>
            <strong>Font:</strong> Inter<br>
            <strong>Primary Color:</strong> #00d4ff (Neon Blue)<br>
            <strong>Background:</strong> #0a0e1a
        </div>
    </div>
    """, unsafe_allow_html=True)

    section_header("Analysis Defaults", "⚙️")
    default_check_leak = st.checkbox("Check for breaches by default", value=True, key="pref_leak")
    default_save_history = st.checkbox("Save to history by default", value=True, key="pref_history")

    if st.button("💾 Save Preferences", use_container_width=True):
        st.success("Preferences saved for this session.")


def _render_about():
    section_header("About Password Checker AI Pro", "ℹ️")

    st.markdown("""
    <div class="glass-card">
        <div style="color:#e2e8f0;line-height:1.7;">
            <h3 style="color:#00d4ff;">Password Strength & Leak Checker AI Pro</h3>
            <p style="color:#94a3b8;">Version 1.0.0 · Enterprise Edition</p>

            <p>A comprehensive password security platform featuring:</p>
            <ul style="color:#cbd5e1;">
                <li>AI-powered password strength analysis with entropy calculation</li>
                <li>Real-time breach checking using Have I Been Pwned k-anonymity API</li>
                <li>Pattern detection (keyboard, sequential, dictionary, dates, personal info)</li>
                <li>Secure password and passphrase generators</li>
                <li>AES-256 encrypted password vault</li>
                <li>Security dashboard with analytics</li>
                <li>Multi-format report export (PDF, CSV, JSON)</li>
                <li>Activity and audit logging</li>
            </ul>

            <h4 style="color:#bd00ff;margin-top:1.5rem;">Security Features</h4>
            <ul style="color:#cbd5e1;">
                <li>bcrypt password hashing (12 rounds)</li>
                <li>PBKDF2 key derivation (600,000 iterations)</li>
                <li>Fernet AES-128-CBC + HMAC-SHA256 encryption</li>
                <li>SHA-1 k-anonymity for breach checking</li>
                <li>SQLAlchemy ORM (SQL injection prevention)</li>
                <li>Input sanitization and validation</li>
            </ul>

            <h4 style="color:#10b981;margin-top:1.5rem;">Tech Stack</h4>
            <p style="color:#94a3b8;">Python 3.13 · Streamlit · SQLAlchemy · Plotly · Cryptography · bcrypt · zxcvbn</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
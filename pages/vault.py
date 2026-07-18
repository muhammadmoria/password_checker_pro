"""Encrypted password vault page."""
import streamlit as st
from components.ui import section_header, info_banner
from services.vault_service import VaultService
from services.auth_service import AuthService
from security.crypto import CryptoManager
from utils.helpers import get_session_user_id
import pyperclip


def render_vault():
    st.markdown('<div class="neon-text-blue" style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">🗝️ Password Vault</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Encrypted storage for your passwords and credentials</p>', unsafe_allow_html=True)

    if not st.session_state.get("vault_unlocked"):
        _render_unlock()
        return

    crypto = st.session_state.get("vault_crypto")
    if not crypto:
        st.error("Vault encryption error. Please re-unlock.")
        st.session_state["vault_unlocked"] = False
        st.rerun()
        return

    vault = VaultService(crypto)

    tab1, tab2 = st.tabs(["📋 All Entries", "➕ Add Entry"])

    with tab1:
        _render_entries(vault)
    with tab2:
        _render_add_form(vault)


def _render_unlock():
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:2rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">🔒</div>
        <div style="font-size:1.2rem;font-weight:600;color:#00d4ff;">Vault Locked</div>
        <div style="color:#94a3b8;margin-top:0.5rem;font-size:0.9rem;">
            Enter your password to decrypt and access your vault entries.<br>
            Your password is used to derive an AES-256 encryption key locally.
        </div>
    </div>
    """, unsafe_allow_html=True)

    password = st.text_input("Enter your password", type="password", placeholder="Your account password", key="vault_pw")

    if st.button("🔓 Unlock Vault", use_container_width=True, type="primary"):
        user_id = get_session_user_id()
        if user_id is None:
            st.error("Not authenticated.")
            return

        auth = AuthService()
        user = auth.get_user_by_id(user_id)
        if not user:
            st.error("User not found.")
            return

        try:
            crypto = auth.get_vault_crypto(password, user)
            # Test decryption with a dummy encrypt/decrypt
            test = crypto.encrypt("test")
            _ = crypto.decrypt(test)

            st.session_state["vault_crypto"] = crypto
            st.session_state["vault_unlocked"] = True
            st.rerun()
        except Exception:
            st.error("Failed to unlock vault. Please check your password.")
            st.session_state["vault_unlocked"] = False

    if st.button("🔒 Lock Vault", key="lock_vault_btn", use_container_width=True):
        st.session_state["vault_unlocked"] = False
        st.session_state["vault_crypto"] = None
        st.rerun()


def _render_entries(vault: VaultService):
    entries = vault.get_entries()

    if not entries:
        st.info("No vault entries yet. Add one in the 'Add Entry' tab.")
        return

    section_header(f"Vault Entries ({len(entries)})", "📋")

    for entry in entries:
        with st.expander(f"🔐 {entry['title']}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Username:** `{entry['username'] or '—'}`")
                st.markdown(f"**Password:** `{'•' * len(entry['password']) if entry['password'] else '—'}`")
                if entry.get("url"):
                    st.markdown(f"**URL:** {entry['url']}")
                if entry.get("notes"):
                    st.markdown(f"**Notes:** {entry['notes']}")
                st.caption(f"Created: {entry.get('created_at', 'N/A')[:19]} | Updated: {entry.get('updated_at', 'N/A')[:19]}")

            with col2:
                if st.button("📋 Copy Password", key=f"copy_{entry['id']}"):
                    try:
                        pyperclip.copy(entry["password"])
                        st.success("Password copied!")
                    except Exception:
                        st.info("Clipboard not available")
                if st.button("📋 Copy Username", key=f"copyu_{entry['id']}"):
                    try:
                        pyperclip.copy(entry["username"])
                        st.success("Username copied!")
                    except Exception:
                        st.info("Clipboard not available")
                if st.button("✏️ Edit", key=f"edit_{entry['id']}"):
                    st.session_state[f"editing_{entry['id']}"] = True
                    st.rerun()
                if st.button("🗑️ Delete", key=f"del_{entry['id']}"):
                    ok, msg = vault.delete_entry(entry["id"])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            if st.session_state.get(f"editing_{entry['id']}"):
                st.markdown("---")
                st.markdown("**Edit Entry**")
                e_title = st.text_input("Title", value=entry["title"], key=f"et_{entry['id']}")
                e_user = st.text_input("Username", value=entry["username"], key=f"eu_{entry['id']}")
                e_pass = st.text_input("Password", value=entry["password"], key=f"ep_{entry['id']}")
                e_url = st.text_input("URL", value=entry.get("url", ""), key=f"eurl_{entry['id']}")
                e_notes = st.text_area("Notes", value=entry.get("notes", ""), key=f"en_{entry['id']}")

                col_s, col_c = st.columns(2)
                with col_s:
                    if st.button("💾 Save", key=f"save_{entry['id']}"):
                        ok, msg = vault.update_entry(entry["id"], e_title, e_user, e_pass, e_url, e_notes)
                        if ok:
                            st.success(msg)
                            st.session_state[f"editing_{entry['id']}"] = False
                            st.rerun()
                        else:
                            st.error(msg)
                with col_c:
                    if st.button("Cancel", key=f"cancel_{entry['id']}"):
                        st.session_state[f"editing_{entry['id']}"] = False
                        st.rerun()


def _generate_vault_password():
    """Callback to generate password before widget renders."""
    from services.generator_service import GeneratorService
    gen = GeneratorService()
    st.session_state["vault_password"] = gen.generate_password(20)


def _render_add_form(vault: VaultService):
    section_header("Add New Entry", "➕")

    title = st.text_input("Title *", placeholder="e.g., GitHub Account", key="vault_title")
    username = st.text_input("Username / Email", placeholder="john@example.com", key="vault_username")
    
    # Use callback for generate button to avoid Session State errors
    password = st.text_input("Password", type="password", placeholder="Enter or generate a password", key="vault_password")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("🎲 Generate Password", use_container_width=True, on_click=_generate_vault_password)
    with col2:
        save_btn = st.button("💾 Save Entry", use_container_width=True, type="primary")

    url = st.text_input("URL (optional)", placeholder="https://github.com", key="vault_url")
    notes = st.text_area("Notes (optional)", placeholder="Additional notes...", key="vault_notes")

    if save_btn:
        if not title.strip():
            st.error("Title is required.")
            return
        ok, msg, _ = vault.add_entry(title, username, password, url, notes)
        if ok:
            st.success(msg)
            # Clear form fields
            st.session_state["vault_title"] = ""
            st.session_state["vault_username"] = ""
            st.session_state["vault_password"] = ""
            st.session_state["vault_url"] = ""
            st.session_state["vault_notes"] = ""
            st.rerun()
        else:
            st.error(msg)
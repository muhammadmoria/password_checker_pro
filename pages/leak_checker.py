"""Dedicated leak checker page."""
import streamlit as st
from components.ui import section_header, info_banner, glass_card
from services.leak_checker import LeakChecker
from security.hashing import sha1_hash


def render_leak_checker():
    st.markdown('<div class="neon-text-blue" style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">🛡️ Password Leak Checker</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Check if your password has been exposed in known data breaches</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div style="color:#94a3b8;font-size:0.9rem;line-height:1.6;">
            <strong style="color:#00d4ff;">🔒 Privacy Guarantee:</strong> Your password is <strong>never</strong> sent to any server.
            We use the <strong>k-anonymity</strong> model with the Have I Been Pwned API:
            <ol style="margin-top:0.5rem;padding-left:1.2rem;">
                <li>Your password is SHA-1 hashed locally on your device</li>
                <li>Only the first 5 characters of the hash are sent to the API</li>
                <li>The API returns all matching hash suffixes</li>
                <li>We compare locally to determine if your password was leaked</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)

    password = st.text_input(
        "Enter a password to check",
        type="password",
        placeholder="Type your password here...",
        key="leak_check_input"
    )

    if st.button("🛡️ Check for Breaches", use_container_width=True, type="primary"):
        if not password:
            st.warning("Please enter a password to check.")
            return

        with st.spinner("Checking breach databases..."):
            checker = LeakChecker()
            result = checker.check_password(password)

        full_hash = sha1_hash(password)
        st.session_state["leak_result"] = {
            "result": result,
            "hash_prefix": full_hash[:5],
            "hash_suffix": full_hash[5:],
        }
        st.rerun()

    leak_data = st.session_state.get("leak_result")
    if leak_data:
        result = leak_data["result"]
        st.markdown("---")
        section_header("Results", "📋")

        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid {result.risk_color};">
            <div style="font-size:0.8rem;color:#64748b;margin-bottom:0.5rem;">SHA-1 Hash (first 5 chars sent): {leak_data['hash_prefix']}••••••••••••••••••••••••••••••</div>
        </div>
        """, unsafe_allow_html=True)

        if result.error:
            info_banner(f"⚠️ {result.error}", "warning")
        elif result.is_leaked:
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid {result.risk_color};">
                <div style="font-size:2rem;font-weight:700;color:{result.risk_color};">🚨 COMPROMISED</div>
                <div style="color:#e2e8f0;margin-top:0.5rem;font-size:1.1rem;">
                    This password has appeared in <strong style="color:{result.risk_color};">{result.breach_count:,}</strong> known data breaches.
                </div>
                <div style="color:#94a3b8;margin-top:0.5rem;">
                    <strong>Risk Level:</strong> <span style="color:{result.risk_color};font-weight:600;">{result.risk_level}</span>
                </div>
                <div style="color:#ef4444;margin-top:1rem;font-size:0.9rem;">
                    ⚠️ <strong>Action Required:</strong> Stop using this password immediately. Change it everywhere it's used and choose a strong, unique replacement.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid {result.risk_color};">
                <div style="font-size:2rem;font-weight:700;color:{result.risk_color};">✅ SAFE</div>
                <div style="color:#e2e8f0;margin-top:0.5rem;font-size:1.1rem;">
                    This password was <strong style="color:{result.risk_color};">not found</strong> in any known data breaches.
                </div>
                <div style="color:#94a3b8;margin-top:0.5rem;">
                    <strong>Risk Level:</strong> <span style="color:{result.risk_color};font-weight:600;">{result.risk_level}</span>
                </div>
                <div style="color:#10b981;margin-top:1rem;font-size:0.9rem;">
                    ✅ While this password hasn't been leaked, always ensure it's also strong and unique.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div style="color:#64748b;font-size:0.8rem;">
                <strong>About the data:</strong> Breach data is sourced from <a href="https://haveibeenpwned.com" style="color:#00d4ff;">Have I Been Pwned</a>,
                which aggregates passwords from publicly disclosed data breaches. The count represents how many times
                this exact password appeared across all tracked breach datasets.
            </div>
        </div>
        """, unsafe_allow_html=True)
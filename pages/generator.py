"""Password and passphrase generator page."""
import streamlit as st
import pyperclip
from components.ui import section_header, glass_card
from services.generator_service import GeneratorService
from ai.analyzer import PasswordAnalyzer
from components.charts import create_score_gauge


def render_generator():
    st.markdown('<div class="neon-text-blue" style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">🔐 Password Generator</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Generate cryptographically secure passwords and passphrases</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔑 Password", "📝 Passphrase", "🔢 PIN"])

    with tab1:
        _render_password_generator()
    with tab2:
        _render_passphrase_generator()
    with tab3:
        _render_pin_generator()


def _render_password_generator():
    gen = GeneratorService()

    col1, col2 = st.columns([2, 1])

    with col1:
        length = st.slider("Password Length", min_value=8, max_value=64, value=16, step=1)

        col_a, col_b = st.columns(2)
        with col_a:
            use_upper = st.checkbox("Uppercase (A-Z)", value=True, key="gen_upper")
            use_lower = st.checkbox("Lowercase (a-z)", value=True, key="gen_lower")
        with col_b:
            use_digits = st.checkbox("Digits (0-9)", value=True, key="gen_digits")
            use_symbols = st.checkbox("Symbols (!@#$)", value=True, key="gen_symbols")

        col_c, col_d = st.columns(2)
        with col_c:
            exclude_similar = st.checkbox("Exclude similar chars (i, l, 1, O, 0)", key="gen_similar")
        with col_d:
            exclude_ambiguous = st.checkbox("Exclude ambiguous chars ({}, [], ...)", key="gen_ambig")

    with col2:
        section_header("Quick Presets", "⚡")
        if st.button("🔒 Strong (16)", use_container_width=True):
            st.session_state["gen_result"] = gen.generate_password(16, True, True, True, True)
            st.rerun()
        if st.button("🛡️ Maximum (32)", use_container_width=True):
            st.session_state["gen_result"] = gen.generate_password(32, True, True, True, True)
            st.rerun()
        if st.button("📝 Memorable (20)", use_container_width=True):
            st.session_state["gen_result"] = gen.generate_password(20, True, True, True, False, exclude_similar=True)
            st.rerun()
        if st.button("🔑 PIN Code (6)", use_container_width=True):
            st.session_state["gen_result"] = gen.generate_pin(6)
            st.rerun()

    if st.button("🎲 Generate Password", use_container_width=True, type="primary"):
        result = gen.generate_password(
            length, use_upper, use_lower, use_digits, use_symbols,
            exclude_similar, exclude_ambiguous
        )
        st.session_state["gen_result"] = result
        st.rerun()

    result = st.session_state.get("gen_result")
    if result:
        st.markdown("---")
        section_header("Generated Password", "✨")

        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:2rem;">
            <div style="font-family:'Courier New',monospace;font-size:1.5rem;font-weight:700;color:#00d4ff;
                        word-break:break-all;letter-spacing:1px;background:rgba(0,212,255,0.05);
                        padding:1rem;border-radius:10px;border:1px solid rgba(0,212,255,0.15);">
                {result}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("📋 Copy", use_container_width=True):
                try:
                    pyperclip.copy(result)
                    st.success("Copied to clipboard!")
                except Exception:
                    st.info(f"Copy manually: {result}")
        with col2:
            if st.button("🔍 Analyze", use_container_width=True):
                analyzer = PasswordAnalyzer()
                analysis = analyzer.analyze(result)
                st.session_state["gen_analysis"] = analysis
                st.rerun()
        with col3:
            if st.button("🎲 Regenerate", use_container_width=True):
                st.session_state["gen_result"] = gen.generate_password(
                    length, use_upper, use_lower, use_digits, use_symbols,
                    exclude_similar, exclude_ambiguous
                )
                st.rerun()

        analysis = st.session_state.get("gen_analysis")
        if analysis:
            st.plotly_chart(create_score_gauge(analysis.score), use_container_width=True)
            st.markdown(f"**Strength:** {analysis.strength_label} | **Entropy:** {analysis.entropy_bits:.1f} bits | **Crack Time:** {analysis.crack_time}")


def _render_passphrase_generator():
    gen = GeneratorService()

    col1, col2 = st.columns(2)
    with col1:
        num_words = st.slider("Number of Words", min_value=2, max_value=10, value=4, step=1)
        separator = st.selectbox("Separator", ["-", "_", ".", " ", "+", "/"], index=0)
    with col2:
        capitalize = st.checkbox("Capitalize words", value=True, key="pp_cap")
        add_number = st.checkbox("Add random number", value=True, key="pp_num")
        add_symbol = st.checkbox("Add random symbol", value=False, key="pp_sym")

    if st.button("📝 Generate Passphrase", use_container_width=True, type="primary"):
        result = gen.generate_passphrase(num_words, separator, capitalize, add_number, add_symbol)
        st.session_state["pp_result"] = result
        st.rerun()

    result = st.session_state.get("pp_result")
    if result:
        st.markdown("---")
        section_header("Generated Passphrase", "✨")
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:2rem;">
            <div style="font-family:'Courier New',monospace;font-size:1.3rem;font-weight:600;color:#bd00ff;
                        word-break:break-all;background:rgba(189,0,255,0.05);
                        padding:1rem;border-radius:10px;border:1px solid rgba(189,0,255,0.15);">
                {result}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📋 Copy Passphrase", use_container_width=True):
            try:
                pyperclip.copy(result)
                st.success("Copied to clipboard!")
            except Exception:
                st.info(f"Copy manually: {result}")

        if st.button("🔍 Analyze Passphrase", use_container_width=True):
            analyzer = PasswordAnalyzer()
            analysis = analyzer.analyze(result)
            st.session_state["pp_analysis"] = analysis
            st.rerun()

        analysis = st.session_state.get("pp_analysis")
        if analysis:
            st.plotly_chart(create_score_gauge(analysis.score), use_container_width=True)
            st.markdown(f"**Strength:** {analysis.strength_label} | **Entropy:** {analysis.entropy_bits:.1f} bits | **Crack Time:** {analysis.crack_time}")


def _render_pin_generator():
    gen = GeneratorService()

    pin_length = st.slider("PIN Length", min_value=4, max_value=12, value=6, step=1)

    if st.button("🔢 Generate PIN", use_container_width=True, type="primary"):
        st.session_state["pin_result"] = gen.generate_pin(pin_length)
        st.rerun()

    result = st.session_state.get("pin_result")
    if result:
        st.markdown("---")
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:2rem;">
            <div style="font-family:'Courier New',monospace;font-size:2rem;font-weight:700;color:#10b981;
                        letter-spacing:8px;background:rgba(16,185,129,0.05);
                        padding:1rem;border-radius:10px;border:1px solid rgba(16,185,129,0.15);">
                {result}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📋 Copy PIN", use_container_width=True):
            try:
                pyperclip.copy(result)
                st.success("Copied to clipboard!")
            except Exception:
                st.info(f"Copy manually: {result}")
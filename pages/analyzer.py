"""Password Analyzer page."""
import streamlit as st
from components.ui import section_header, info_banner, glass_card
from components.charts import create_score_gauge, create_strength_bar, create_entropy_chart, create_radar_chart
from services.password_service import PasswordService
from services.export_service import ExportService


def render_analyzer():
    st.markdown('<div class="neon-text-blue" style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">🔍 Password Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">AI-powered deep analysis of your password security</p>', unsafe_allow_html=True)

    service = PasswordService()
    exporter = ExportService()

    col_input, col_options = st.columns([3, 2])

    with col_input:
        password = st.text_input(
            "Enter a password to analyze",
            type="password",
            placeholder="Type your password here...",
            help="Your password is never sent to any server in plaintext. Leak checking uses SHA-1 k-anonymity."
        )

    with col_options:
        st.markdown("**Personal Information Check**")
        with st.expander("Add personal info (optional)"):
            pi_name = st.text_input("Name", placeholder="John", key="pi_name")
            pi_birth = st.text_input("Birth year", placeholder="1990", key="pi_birth")
            pi_email = st.text_input("Email", placeholder="john@example.com", key="pi_email")

        check_leak = st.checkbox("Check for data breaches", value=True)
        save_history = st.checkbox("Save to history", value=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_btn = st.button("🚀 Analyze Password", use_container_width=True, type="primary")

    if analyze_btn and password:
        personal_info = {}
        if pi_name:
            personal_info["name"] = pi_name
        if pi_birth:
            personal_info["birth_year"] = pi_birth
        if pi_email:
            personal_info["email"] = pi_email

        with st.spinner("Analyzing password..."):
            result = service.analyze_password(
                password,
                personal_info=personal_info if personal_info else None,
                check_leak=check_leak,
                save_history=save_history,
            )

        st.session_state["last_analysis"] = result
        st.rerun()

    result = st.session_state.get("last_analysis")
    if result:
        _render_analysis_result(result, exporter)


def _render_analysis_result(result: dict, exporter: ExportService):
    analysis = result["analysis"]

    st.markdown("---")
    section_header("Analysis Results", "📋")

    # Top row: gauge and radar
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_score_gauge(analysis["score"]), use_container_width=True)
        st.plotly_chart(create_strength_bar(analysis["strength_label"], analysis["score"]), use_container_width=True)

    with col2:
        st.plotly_chart(create_radar_chart(analysis), use_container_width=True)

    # Character composition
    section_header("Character Composition", "🔤")
    comp_cols = st.columns(4)
    with comp_cols[0]:
        st.metric("Length", str(analysis["length"]))
    with comp_cols[1]:
        st.metric("Charset Size", str(analysis["charset_size"]))
    with comp_cols[2]:
        st.metric("Entropy", f"{analysis['entropy_bits']:.1f} bits")
    with comp_cols[3]:
        st.metric("Diversity", f"{analysis['character_diversity']:.1%}")

    comp_checks = st.columns(4)
    with comp_checks[0]:
        st.metric("Lowercase", "✅" if analysis["has_lowercase"] else "❌")
    with comp_checks[1]:
        st.metric("Uppercase", "✅" if analysis["has_uppercase"] else "❌")
    with comp_checks[2]:
        st.metric("Digits", "✅" if analysis["has_digits"] else "❌")
    with comp_checks[3]:
        st.metric("Symbols", "✅" if analysis["has_symbols"] else "❌")

    # Entropy chart
    st.plotly_chart(create_entropy_chart(analysis["entropy_bits"]), use_container_width=True)

    # Breach check
    if result.get("breach_count") is not None:
        section_header("Breach Check Results", "🛡️")
        breach_count = result["breach_count"]
        risk_level = result["risk_level"]
        risk_color = result["risk_color"]

        if result.get("leak_error"):
            info_banner(f"⚠️ {result['leak_error']}", "warning")
        elif breach_count > 0:
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid {risk_color};">
                <div style="font-size:1.5rem;font-weight:700;color:{risk_color};">{breach_count:,} breaches found</div>
                <div style="color:#94a3b8;margin-top:0.5rem;">Risk Level: <span style="color:{risk_color};font-weight:600;">{risk_level}</span></div>
                <div style="color:#64748b;margin-top:0.5rem;font-size:0.85rem;">
                    This password has been seen {breach_count:,} times in known data breaches.
                    It should never be used.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid {risk_color};">
                <div style="font-size:1.5rem;font-weight:700;color:{risk_color};">✅ No breaches found</div>
                <div style="color:#94a3b8;margin-top:0.5rem;">This password has not been found in known data breaches.</div>
            </div>
            """, unsafe_allow_html=True)

    # Findings
    findings = analysis.get("pattern_findings", [])
    if findings:
        section_header("Security Findings", "⚠️")
        for f in findings:
            st.markdown(f"• ⚠️ {f}")

    # Suggestions
    suggestions = analysis.get("suggestions", [])
    if suggestions:
        section_header("Recommendations", "💡")
        for s in suggestions:
            st.markdown(f"• ✅ {s}")

    # AI Explanation
    section_header("AI Explanation", "🤖")
    st.markdown(f"""
    <div class="glass-card">
        <div style="color:#e2e8f0;line-height:1.7;font-size:0.95rem;">
        {result.get("explanation", "No explanation available.")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Export
    section_header("Export Report", "📤")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "📄 Download PDF",
            data=exporter.export_pdf(result, "Password Analysis Report"),
            file_name="password_analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "📊 Download JSON",
            data=exporter.export_json(result),
            file_name="password_analysis.json",
            mime="application/json",
            use_container_width=True,
        )
    with col3:
        flat = {"score": analysis["score"], "strength": analysis["strength_label"], "entropy": analysis["entropy_bits"],
                "crack_time": analysis["crack_time"], "breach_count": result.get("breach_count", "N/A")}
        st.download_button(
            "📋 Download CSV",
            data=exporter.export_csv([flat]),
            file_name="password_analysis.csv",
            mime="text/csv",
            use_container_width=True,
        )
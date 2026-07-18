"""Password history page."""
import streamlit as st
from components.ui import section_header
from services.password_service import PasswordService
from services.export_service import ExportService


def render_history():
    st.markdown('<div class="neon-text-blue" style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">📜 Password History</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Your password analysis history (masked for security)</p>', unsafe_allow_html=True)

    service = PasswordService()
    exporter = ExportService()

    history = service.get_history(limit=100)

    if not history:
        st.info("No history yet. Analyze some passwords to build your history.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entries", len(history))
    with col2:
        avg_score = sum(h.get("score", 0) for h in history) / len(history)
        st.metric("Average Score", f"{avg_score:.0f}")
    with col3:
        leaked = sum(1 for h in history if h.get("breach_count") and h["breach_count"] > 0)
        st.metric("Leaked Passwords", leaked)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Export JSON", use_container_width=True):
            st.download_button(
                "⬇️ Download",
                data=exporter.export_json(history),
                file_name="password_history.json",
                mime="application/json",
                use_container_width=True,
            )
    with col2:
        if st.button("📋 Export CSV", use_container_width=True):
            flat = []
            for h in history:
                flat.append({
                    "timestamp": h.get("timestamp", ""),
                    "masked_password": h.get("password_masked", ""),
                    "score": h.get("score", 0),
                    "strength": h.get("strength_label", ""),
                    "entropy": h.get("entropy", ""),
                    "crack_time": h.get("crack_time", ""),
                    "breach_count": h.get("breach_count", ""),
                })
            st.download_button(
                "⬇️ Download",
                data=exporter.export_csv(flat),
                file_name="password_history.csv",
                mime="text/csv",
                use_container_width=True,
            )

    if st.button("🗑️ Clear All History", use_container_width=True):
        count = service.clear_history()
        st.success(f"Cleared {count} entries.")
        st.rerun()

    st.markdown("---")
    section_header("History Entries", "📋")

    for entry in reversed(history):
        score = entry.get("score", 0)
        label = entry.get("strength_label", "Unknown")

        if score >= 75:
            color = "#10b981"
        elif score >= 60:
            color = "#eab308"
        elif score >= 40:
            color = "#f59e0b"
        else:
            color = "#ef4444"

        breach = entry.get("breach_count")
        breach_text = ""
        if breach is not None and breach > 0:
            breach_text = f" | 🚨 Breached: {breach:,}"

        with st.expander(
            f"{'🔴' if score < 40 else '🟡' if score < 60 else '🟢'} {entry.get('password_masked', '***')} — {label} ({score}/100){breach_text}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Timestamp:** {entry.get('timestamp', 'N/A')[:19]}")
                st.markdown(f"**Score:** {score}/100")
                st.markdown(f"**Strength:** {label}")
                st.markdown(f"**Entropy:** {entry.get('entropy', 'N/A')} bits")
            with col2:
                st.markdown(f"**Crack Time:** {entry.get('crack_time', 'N/A')}")
                st.markdown(f"**Breach Count:** {breach if breach is not None else 'Not checked'}")
                analysis = entry.get("analysis", {})
                findings = analysis.get("pattern_findings", [])
                if findings:
                    st.markdown("**Findings:**")
                    for f in findings:
                        st.markdown(f"  • {f}")
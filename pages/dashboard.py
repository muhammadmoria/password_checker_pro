"""Dashboard page - security overview."""
import streamlit as st
from components.ui import section_header, metric_card, glass_card
from components.charts import create_score_trend_chart, create_strength_distribution_chart
from analytics.stats import StatsCalculator


def render_dashboard():
    st.markdown('<div class="neon-text-blue" style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">📊 Security Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">Overview of your password security posture</p>', unsafe_allow_html=True)

    stats = StatsCalculator()
    data = stats.get_user_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Analyses", str(data.get("total_analyses", 0)), "🔍", "#00d4ff")
    with col2:
        avg = data.get("avg_score", 0)
        metric_card("Avg Score", f"{avg:.0f}/100", "📈", "#10b981" if avg >= 60 else "#f59e0b")
    with col3:
        metric_card("Leaked Passwords", str(data.get("leaked_count", 0)), "⚠️", "#ef4444")
    with col4:
        metric_card("Vault Entries", str(data.get("vault_count", 0)), "🗝️", "#bd00ff")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        section_header("Score Trend", "📈")
        scores = data.get("score_distribution", [])
        if scores:
            st.plotly_chart(create_score_trend_chart(list(reversed(scores))), use_container_width=True)
        else:
            st.info("No analysis data yet. Run a password analysis to see trends.")

    with col_right:
        section_header("Strength Distribution", "🥧")
        dist = data.get("strength_distribution", {})
        if dist:
            st.plotly_chart(create_strength_distribution_chart(dist), use_container_width=True)
        else:
            st.info("No strength data available yet.")

    st.markdown("---")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        metric_card("Weak Passwords", str(data.get("weak_count", 0)), "🔴", "#ef4444")
    with col_b:
        metric_card("Good Passwords", str(data.get("good_count", 0)), "🟡", "#eab308")
    with col_c:
        metric_card("Strong Passwords", str(data.get("strong_count", 0)), "🟢", "#10b981")

    st.markdown("---")

    section_header("Quick Actions", "⚡")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Analyze Password", use_container_width=True):
            st.session_state["page"] = "Analyzer"
            st.rerun()
    with col2:
        if st.button("🔐 Generate Password", use_container_width=True):
            st.session_state["page"] = "Generator"
            st.rerun()
    with col3:
        if st.button("🛡️ Check Leaks", use_container_width=True):
            st.session_state["page"] = "Leak Checker"
            st.rerun()
"""Admin dashboard page."""
import streamlit as st
from components.ui import section_header, metric_card
from services.auth_service import AuthService
from services.activity_service import ActivityService
from analytics.stats import StatsCalculator
from services.export_service import ExportService


def render_admin():
    user = st.session_state.get("current_user")
    if not user or not user.get("is_admin"):
        st.error("Access denied. Administrator privileges required.")
        return

    st.markdown('<div class="neon-text-purple" style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">👑 Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8;margin-bottom:1.5rem;">System administration and monitoring</p>', unsafe_allow_html=True)

    stats = StatsCalculator()
    admin_data = stats.get_admin_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Users", str(admin_data.get("total_users", 0)), "👥", "#00d4ff")
    with col2:
        metric_card("Active Users", str(admin_data.get("active_users", 0)), "✅", "#10b981")
    with col3:
        metric_card("Total Analyses", str(admin_data.get("total_analyses", 0)), "🔍", "#bd00ff")
    with col4:
        metric_card("Vault Entries", str(admin_data.get("total_vault_entries", 0)), "🗝️", "#f59e0b")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "📊 Activity Logs", "🔒 Audit Logs", "📈 System Stats"])

    with tab1:
        _render_users_tab()
    with tab2:
        _render_activity_tab()
    with tab3:
        _render_audit_tab()
    with tab4:
        _render_system_stats(admin_data)


def _render_users_tab():
    section_header("User Management", "👥")
    auth = AuthService()
    users = auth.get_all_users()
    exporter = ExportService()

    if st.button("📊 Export Users (JSON)"):
        st.download_button(
            "⬇️ Download",
            data=exporter.export_json([u.to_dict() for u in users]),
            file_name="users_export.json",
            mime="application/json",
        )

    st.markdown("---")

    for u in users:
        with st.expander(f"{'👑' if u.is_admin else '👤'} {u.username} ({'Admin' if u.is_admin else 'User'})"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**User ID:** {u.id}")
                st.markdown(f"**Public ID:** {u.public_id}")
                st.markdown(f"**Role:** {'Administrator' if u.is_admin else 'Standard User'}")
                st.markdown(f"**Status:** {'Active' if u.is_active else 'Inactive'}")
                st.markdown(f"**Created:** {u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else 'N/A'}")
                st.markdown(f"**Last Login:** {u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else 'Never'}")
            with col2:
                current_user = st.session_state.get("current_user")
                if current_user and current_user["id"] != u.id:
                    if st.button("Toggle Active", key=f"toggle_{u.id}"):
                        ok, msg = auth.deactivate_user(u.id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.info("This is you")


def _render_activity_tab():
    section_header("Activity Logs", "📊")
    activity = ActivityService()
    logs = activity.get_activity_logs(limit=200)

    if not logs:
        st.info("No activity logs found.")
        return

    exporter = ExportService()
    if st.button("📊 Export Activity (CSV)"):
        st.download_button(
            "⬇️ Download",
            data=exporter.export_csv(logs),
            file_name="activity_logs.csv",
            mime="text/csv",
        )

    st.markdown("---")

    for log in logs[:100]:
        ts = log.get("timestamp", "")[:19] if log.get("timestamp") else "N/A"
        action = log.get("action", "Unknown")
        details = log.get("details", "")
        st.markdown(f"""
        <div class="glass-card" style="padding:0.75rem 1rem;margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="color:#00d4ff;font-weight:600;">{action}</span>
                    <span style="color:#64748b;margin-left:0.5rem;font-size:0.85rem;">{details}</span>
                </div>
                <div style="color:#64748b;font-size:0.8rem;">{ts}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_audit_tab():
    section_header("Audit Logs", "🔒")
    activity = ActivityService()
    logs = activity.get_audit_logs(limit=200)

    if not logs:
        st.info("No audit logs found.")
        return

    exporter = ExportService()
    if st.button("📊 Export Audit (CSV)"):
        st.download_button(
            "⬇️ Download",
            data=exporter.export_csv(logs),
            file_name="audit_logs.csv",
            mime="text/csv",
        )

    st.markdown("---")

    severity_colors = {
        "info": "#00d4ff",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "critical": "#dc2626",
    }

    for log in logs[:100]:
        ts = log.get("timestamp", "")[:19] if log.get("timestamp") else "N/A"
        event = log.get("event_type", "Unknown")
        desc = log.get("description", "")
        severity = log.get("severity", "info")
        color = severity_colors.get(severity, "#64748b")

        st.markdown(f"""
        <div class="glass-card" style="padding:0.75rem 1rem;margin-bottom:0.5rem;border-left:3px solid {color};">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="color:{color};font-weight:600;text-transform:uppercase;font-size:0.75rem;">{severity}</span>
                    <span style="color:#00d4ff;font-weight:600;margin-left:0.5rem;">{event}</span>
                    <span style="color:#94a3b8;margin-left:0.5rem;font-size:0.85rem;">{desc}</span>
                </div>
                <div style="color:#64748b;font-size:0.8rem;">{ts}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_system_stats(admin_data: dict):
    section_header("System Statistics", "📈")

    col1, col2 = st.columns(2)
    with col1:
        metric_card("Total Activities", str(admin_data.get("total_activities", 0)), "📊", "#00d4ff")
        metric_card("Admin Users", str(admin_data.get("admin_users", 0)), "👑", "#bd00ff")
    with col2:
        metric_card("Total Audit Events", str(admin_data.get("total_audits", 0)), "🔒", "#10b981")
        metric_card("Total Vault Entries", str(admin_data.get("total_vault_entries", 0)), "🗝️", "#f59e0b")

    st.markdown("---")
    section_header("Recent Users", "🆕")

    recent = admin_data.get("recent_users", [])
    for u in recent:
        st.markdown(f"""
        <div class="glass-card" style="padding:0.75rem 1rem;margin-bottom:0.5rem;">
            <span style="color:#e2e8f0;font-weight:600;">{u.get('username', 'Unknown')}</span>
            <span style="color:#64748b;margin-left:0.5rem;font-size:0.85rem;">
                {'Admin' if u.get('is_admin') else 'User'} ·
                Created: {u.get('created_at', 'N/A')[:19] if u.get('created_at') else 'N/A'}
            </span>
        </div>
        """, unsafe_allow_html=True)
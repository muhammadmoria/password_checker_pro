"""Activity and audit log services."""
import logging
from database.connection import get_session_factory
from models.models import ActivityLog, AuditLog

logger = logging.getLogger(__name__)


class ActivityService:
    """Manage activity and audit logs."""

    def get_activity_logs(self, limit: int = 100) -> list[dict]:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            logs = (
                session.query(ActivityLog)
                .order_by(ActivityLog.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [l.to_dict() for l in logs]
        finally:
            session.close()

    def get_audit_logs(self, limit: int = 100) -> list[dict]:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            logs = (
                session.query(AuditLog)
                .order_by(AuditLog.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [l.to_dict() for l in logs]
        finally:
            session.close()

    def get_user_activity(self, user_id: int, limit: int = 50) -> list[dict]:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            logs = (
                session.query(ActivityLog)
                .filter(ActivityLog.user_id == user_id)
                .order_by(ActivityLog.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [l.to_dict() for l in logs]
        finally:
            session.close()

    def log_activity(self, user_id: int | None, action: str, details: str = ""):
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            log = ActivityLog(user_id=user_id, action=action, details=details)
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Failed to log activity: %s", e)
        finally:
            session.close()

    def log_audit(self, event_type: str, description: str, user_id: int | None = None, severity: str = "info"):
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            log = AuditLog(event_type=event_type, description=description, user_id=user_id, severity=severity)
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Failed to log audit: %s", e)
        finally:
            session.close()
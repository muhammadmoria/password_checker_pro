"""Statistics and analytics calculator."""
import logging
from collections import Counter
from database.connection import get_session_factory
from models.models import PasswordHistory, VaultEntry, User, ActivityLog, AuditLog
from utils.helpers import get_session_user_id

logger = logging.getLogger(__name__)


class StatsCalculator:
    """Calculate dashboard statistics."""

    def get_user_stats(self) -> dict:
        user_id = get_session_user_id()
        if user_id is None:
            return {}

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            history = (
                session.query(PasswordHistory)
                .filter(PasswordHistory.user_id == user_id)
                .order_by(PasswordHistory.timestamp.desc())
                .all()
            )

            vault_count = session.query(VaultEntry).filter(VaultEntry.user_id == user_id).count()

            if not history:
                return {
                    "total_analyses": 0,
                    "avg_score": 0,
                    "weak_count": 0,
                    "strong_count": 0,
                    "leaked_count": 0,
                    "vault_count": vault_count,
                    "score_distribution": [],
                    "strength_distribution": {},
                    "recent_scores": [],
                }

            scores = [h.score for h in history]
            labels = [h.strength_label for h in history]
            breach_counts = [h.breach_count for h in history if h.breach_count is not None]

            label_counter = Counter(labels)

            return {
                "total_analyses": len(history),
                "avg_score": sum(scores) / len(scores),
                "max_score": max(scores),
                "min_score": min(scores),
                "weak_count": sum(1 for s in scores if s < 40),
                "fair_count": sum(1 for s in scores if 40 <= s < 60),
                "good_count": sum(1 for s in scores if 60 <= s < 75),
                "strong_count": sum(1 for s in scores if s >= 75),
                "leaked_count": sum(1 for h in history if h.breach_count and h.breach_count > 0),
                "vault_count": vault_count,
                "score_distribution": scores[::-1][:20],
                "strength_distribution": dict(label_counter),
                "recent_scores": [{"timestamp": h.timestamp.isoformat(), "score": h.score, "label": h.strength_label} for h in history[:20]],
            }
        finally:
            session.close()

    def get_admin_stats(self) -> dict:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            total_users = session.query(User).count()
            active_users = session.query(User).filter(User.is_active == True).count()
            admin_users = session.query(User).filter(User.is_admin == True).count()
            total_analyses = session.query(PasswordHistory).count()
            total_vault_entries = session.query(VaultEntry).count()
            total_activities = session.query(ActivityLog).count()
            total_audits = session.query(AuditLog).count()

            recent_users = (
                session.query(User)
                .order_by(User.created_at.desc())
                .limit(10)
                .all()
            )

            return {
                "total_users": total_users,
                "active_users": active_users,
                "admin_users": admin_users,
                "total_analyses": total_analyses,
                "total_vault_entries": total_vault_entries,
                "total_activities": total_activities,
                "total_audits": total_audits,
                "recent_users": [u.to_dict() for u in recent_users],
            }
        finally:
            session.close()
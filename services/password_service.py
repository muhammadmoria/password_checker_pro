"""Password analysis service that coordinates AI analysis and leak checking."""
import json
import logging
from datetime import datetime, timezone

from ai.analyzer import PasswordAnalyzer, AnalysisResult
from ai.explainer import explain_analysis
from services.leak_checker import LeakChecker
from database.connection import get_session_factory
from models.models import PasswordHistory, ActivityLog
from utils.helpers import get_session_user_id

logger = logging.getLogger(__name__)


class PasswordService:
    """High-level service for password analysis and history management."""

    def __init__(self):
        self.analyzer = PasswordAnalyzer()
        self.leak_checker = LeakChecker()

    def analyze_password(
        self,
        password: str,
        personal_info: dict[str, str] | None = None,
        check_leak: bool = True,
        save_history: bool = True,
    ) -> dict:
        """Analyze a password and optionally check for leaks."""
        analysis = self.analyzer.analyze(password, personal_info)
        explanation = explain_analysis(analysis)

        breach_count = None
        leak_error = None
        risk_level = "Not Checked"
        risk_color = "#6b7280"

        if check_leak:
            leak_result = self.leak_checker.check_password(password)
            breach_count = leak_result.breach_count
            leak_error = leak_result.error
            risk_level = leak_result.risk_level
            risk_color = leak_result.risk_color

        if save_history:
            self._save_history(analysis, breach_count)

        return {
            "analysis": analysis.to_dict(),
            "explanation": explanation,
            "breach_count": breach_count,
            "leak_error": leak_error,
            "risk_level": risk_level,
            "risk_color": risk_color,
        }

    def _save_history(self, analysis: AnalysisResult, breach_count: int | None):
        user_id = get_session_user_id()
        if user_id is None:
            return

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            entry = PasswordHistory(
                user_id=user_id,
                timestamp=datetime.now(timezone.utc),
                password_masked=analysis.password_masked,
                score=analysis.score,
                entropy=f"{analysis.entropy_bits:.2f}",
                crack_time=analysis.crack_time,
                breach_count=breach_count,
                strength_label=analysis.strength_label,
                analysis_json=json.dumps(analysis.to_dict()),
            )
            session.add(entry)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Failed to save password history: %s", e)
        finally:
            session.close()

    def get_history(self, limit: int = 50) -> list[dict]:
        user_id = get_session_user_id()
        if user_id is None:
            return []

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            entries = (
                session.query(PasswordHistory)
                .filter(PasswordHistory.user_id == user_id)
                .order_by(PasswordHistory.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [e.to_dict() for e in entries]
        finally:
            session.close()

    def clear_history(self) -> int:
        user_id = get_session_user_id()
        if user_id is None:
            return 0

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            count = (
                session.query(PasswordHistory)
                .filter(PasswordHistory.user_id == user_id)
                .delete()
            )
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            logger.error("Failed to clear history: %s", e)
            return 0
        finally:
            session.close()
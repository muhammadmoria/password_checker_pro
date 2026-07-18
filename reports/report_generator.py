"""Report generation coordinator."""
import logging
from services.export_service import ExportService

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate reports in multiple formats."""

    def __init__(self):
        self.exporter = ExportService()

    def generate_json_report(self, data: dict) -> bytes:
        return self.exporter.export_json(data)

    def generate_csv_report(self, data: list[dict]) -> bytes:
        return self.exporter.export_csv(data)

    def generate_pdf_report(self, data: dict, title: str = "Password Analysis Report") -> bytes:
        return self.exporter.export_pdf(data, title)

    def generate_history_report(self, history: list[dict]) -> dict:
        """Build a summary report from password history."""
        if not history:
            return {
                "total": 0,
                "summary": "No password history available.",
            }

        scores = [h.get("score", 0) for h in history]
        leaked = [h for h in history if h.get("breach_count", 0) and h["breach_count"] > 0]

        return {
            "total": len(history),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "leaked_count": len(leaked),
            "history": history,
        }
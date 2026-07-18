"""Encrypted password vault service."""
import logging
from datetime import datetime, timezone

from database.connection import get_session_factory
from models.models import VaultEntry
from security.crypto import CryptoManager
from utils.helpers import get_session_user_id

logger = logging.getLogger(__name__)


class VaultService:
    """Manage encrypted vault entries."""

    def __init__(self, crypto: CryptoManager):
        self.crypto = crypto

    def add_entry(
        self,
        title: str,
        username: str = "",
        password: str = "",
        url: str = "",
        notes: str = "",
    ) -> tuple[bool, str, VaultEntry | None]:
        user_id = get_session_user_id()
        if user_id is None:
            return False, "Not authenticated.", None

        if not title.strip():
            return False, "Title is required.", None

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            entry = VaultEntry(
                user_id=user_id,
                title=title.strip(),
                username_encrypted=self.crypto.encrypt(username) if username else "",
                password_encrypted=self.crypto.encrypt(password) if password else "",
                url_encrypted=self.crypto.encrypt(url) if url else "",
                notes_encrypted=self.crypto.encrypt(notes) if notes else "",
            )
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return True, "Vault entry created.", entry
        except Exception as e:
            session.rollback()
            logger.error("Vault add error: %s", e)
            return False, str(e), None
        finally:
            session.close()

    def update_entry(
        self,
        entry_id: int,
        title: str,
        username: str = "",
        password: str = "",
        url: str = "",
        notes: str = "",
    ) -> tuple[bool, str]:
        user_id = get_session_user_id()
        if user_id is None:
            return False, "Not authenticated."

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            entry = session.get(VaultEntry, entry_id)
            if not entry or entry.user_id != user_id:
                return False, "Entry not found."

            entry.title = title.strip()
            entry.username_encrypted = self.crypto.encrypt(username) if username else ""
            entry.password_encrypted = self.crypto.encrypt(password) if password else ""
            entry.url_encrypted = self.crypto.encrypt(url) if url else ""
            entry.notes_encrypted = self.crypto.encrypt(notes) if notes else ""
            entry.updated_at = datetime.now(timezone.utc)

            session.commit()
            return True, "Entry updated."
        except Exception as e:
            session.rollback()
            logger.error("Vault update error: %s", e)
            return False, str(e)
        finally:
            session.close()

    def delete_entry(self, entry_id: int) -> tuple[bool, str]:
        user_id = get_session_user_id()
        if user_id is None:
            return False, "Not authenticated."

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            entry = session.get(VaultEntry, entry_id)
            if not entry or entry.user_id != user_id:
                return False, "Entry not found."
            session.delete(entry)
            session.commit()
            return True, "Entry deleted."
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_entries(self) -> list[dict]:
        """Return all vault entries with decrypted fields."""
        user_id = get_session_user_id()
        if user_id is None:
            return []

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            entries = (
                session.query(VaultEntry)
                .filter(VaultEntry.user_id == user_id)
                .order_by(VaultEntry.title.asc())
                .all()
            )
            result = []
            for e in entries:
                try:
                    decrypted = {
                        "username": self.crypto.decrypt(e.username_encrypted) if e.username_encrypted else "",
                        "password": self.crypto.decrypt(e.password_encrypted) if e.password_encrypted else "",
                        "url": self.crypto.decrypt(e.url_encrypted) if e.url_encrypted else "",
                        "notes": self.crypto.decrypt(e.notes_encrypted) if e.notes_encrypted else "",
                    }
                except ValueError:
                    decrypted = {
                        "username": "[decryption failed]",
                        "password": "[decryption failed]",
                        "url": "",
                        "notes": "",
                    }
                result.append({
                    "id": e.id,
                    "title": e.title,
                    "username": decrypted["username"],
                    "password": decrypted["password"],
                    "url": decrypted["url"],
                    "notes": decrypted["notes"],
                    "created_at": e.created_at.isoformat() if e.created_at else "",
                    "updated_at": e.updated_at.isoformat() if e.updated_at else "",
                })
            return result
        finally:
            session.close()

    def get_entry_count(self) -> int:
        user_id = get_session_user_id()
        if user_id is None:
            return 0
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            return session.query(VaultEntry).filter(VaultEntry.user_id == user_id).count()
        finally:
            session.close()
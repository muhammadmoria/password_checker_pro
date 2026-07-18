"""User authentication and session management service."""
import os
import logging
from datetime import datetime, timezone

from database.connection import get_session_factory
from models.models import User, ActivityLog, AuditLog
from security.hashing import hash_password_bcrypt, verify_password_bcrypt, generate_salt
from security.crypto import CryptoManager
from security.validation import validate_username, validate_password_length
from config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Handle user registration, authentication, and session state."""

    def register(self, username: str, password: str, is_admin: bool = False) -> tuple[bool, str, User | None]:
        valid, msg = validate_username(username)
        if not valid:
            return False, msg, None

        valid, msg = validate_password_length(password, min_length=8)
        if not valid:
            return False, msg, None

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                return False, "Username already exists.", None

            salt = generate_salt(settings.pbkdf2_salt_size)
            user = User(
                username=username,
                password_hash=hash_password_bcrypt(password),
                is_admin=is_admin,
                is_active=True,
                vault_salt=salt,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            self._log_activity(session, user.id, "register", f"User '{username}' registered.")
            self._log_audit(session, "user_registered", f"New user registered: {username}", user.id, "info")
            session.commit()

            return True, "Registration successful.", user
        except Exception as e:
            session.rollback()
            logger.error("Registration error: %s", e)
            return False, f"Registration failed: {e}", None
        finally:
            session.close()

    def login(self, username: str, password: str) -> tuple[bool, str, User | None]:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == username).first()
            if not user:
                self._log_audit(session, "login_failed", f"Login attempt for unknown user: {username}", None, "warning")
                session.commit()
                return False, "Invalid username or password.", None

            if not user.is_active:
                return False, "Account is deactivated.", None

            if not verify_password_bcrypt(password, user.password_hash):
                self._log_audit(session, "login_failed", f"Failed login for user: {username}", user.id, "warning")
                session.commit()
                return False, "Invalid username or password.", None

            user.last_login = datetime.now(timezone.utc)
            self._log_activity(session, user.id, "login", f"User '{username}' logged in.")
            self._log_audit(session, "login_success", f"User logged in: {username}", user.id, "info")
            session.commit()

            return True, "Login successful.", user
        except Exception as e:
            session.rollback()
            logger.error("Login error: %s", e)
            return False, f"Login failed: {e}", None
        finally:
            session.close()

    def change_password(self, user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
        valid, msg = validate_password_length(new_password, min_length=8)
        if not valid:
            return False, msg

        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found."

            if not verify_password_bcrypt(old_password, user.password_hash):
                self._log_audit(session, "password_change_failed", "Failed password change: wrong old password.", user_id, "warning")
                session.commit()
                return False, "Current password is incorrect."

            user.password_hash = hash_password_bcrypt(new_password)
            new_salt = generate_salt(settings.pbkdf2_salt_size)
            user.vault_salt = new_salt

            self._log_activity(session, user_id, "password_change", "Password changed successfully.")
            self._log_audit(session, "password_changed", "User changed their password.", user_id, "info")
            session.commit()
            return True, "Password changed successfully."
        except Exception as e:
            session.rollback()
            logger.error("Password change error: %s", e)
            return False, f"Failed to change password: {e}"
        finally:
            session.close()

    def get_vault_crypto(self, password: str, user: User) -> CryptoManager:
        """Create a CryptoManager using the user's password and stored salt."""
        salt = bytes.fromhex(user.vault_salt) if user.vault_salt else None
        return CryptoManager(password, salt=salt)

    def get_user_by_id(self, user_id: int) -> User | None:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            return session.get(User, user_id)
        finally:
            session.close()

    def get_user_by_username(self, username: str) -> User | None:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()

    def get_all_users(self) -> list[User]:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            return session.query(User).order_by(User.created_at.desc()).all()
        finally:
            session.close()

    def deactivate_user(self, user_id: int) -> tuple[bool, str]:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            user = session.get(User, user_id)
            if not user:
                return False, "User not found."
            user.is_active = not user.is_active
            self._log_audit(session, "user_status_changed", f"User '{user.username}' active={user.is_active}", user_id, "info")
            session.commit()
            status = "activated" if user.is_active else "deactivated"
            return True, f"User {status} successfully."
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def _log_activity(session, user_id: int, action: str, details: str):
        log = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=None,
        )
        session.add(log)

    @staticmethod
    def _log_audit(session, event_type: str, description: str, user_id: int | None, severity: str):
        log = AuditLog(
            event_type=event_type,
            description=description,
            user_id=user_id,
            severity=severity,
        )
        session.add(log)
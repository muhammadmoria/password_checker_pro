"""Tests for database models."""
import pytest
from database.connection import get_engine, get_session_factory, init_database
from models.models import User, PasswordHistory, VaultEntry, ActivityLog, AuditLog
from security.hashing import hash_password_bcrypt


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Initialize database before tests."""
    init_database()


class TestUserModel:
    def test_create_user(self):
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            user = User(
                username="testuser_models",
                password_hash=hash_password_bcrypt("TestPass123!"),
                is_admin=False,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            assert user.id is not None
            assert user.username == "testuser_models"
            assert user.is_admin is False
            assert user.is_active is True
            assert user.public_id is not None
            assert user.created_at is not None
        finally:
            session.query(User).filter(User.username == "testuser_models").delete()
            session.commit()
            session.close()

    def test_user_to_dict(self):
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            user = User(
                username="dict_test_user",
                password_hash=hash_password_bcrypt("Test123!"),
                is_admin=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            d = user.to_dict()
            assert d["username"] == "dict_test_user"
            assert d["is_admin"] is True
            assert "password_hash" not in d
        finally:
            session.query(User).filter(User.username == "dict_test_user").delete()
            session.commit()
            session.close()


class TestAuditLog:
    def test_create_audit_log(self):
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            log = AuditLog(
                event_type="test_event",
                description="Test audit log entry",
                severity="info",
            )
            session.add(log)
            session.commit()
            session.refresh(log)

            assert log.id is not None
            assert log.event_type == "test_event"
            assert log.timestamp is not None
        finally:
            session.query(AuditLog).filter(AuditLog.event_type == "test_event").delete()
            session.commit()
            session.close()


class TestActivityLog:
    def test_create_activity_log(self):
        SessionLocal = get_session_factory()
        session = SessionLocal()
        try:
            log = ActivityLog(
                user_id=None,
                action="test_action",
                details="Test activity log",
            )
            session.add(log)
            session.commit()
            session.refresh(log)

            assert log.id is not None
            assert log.action == "test_action"
        finally:
            session.query(ActivityLog).filter(ActivityLog.action == "test_action").delete()
            session.commit()
            session.close()
"""SQLAlchemy ORM models."""
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def _utcnow():
    return datetime.now(timezone.utc)


def _uuid_str():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(String(36), unique=True, default=_uuid_str, nullable=False)
    username = Column(String(128), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    vault_salt = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    password_history = relationship("PasswordHistory", back_populates="user", cascade="all, delete-orphan")
    vault_entries = relationship("VaultEntry", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "public_id": self.public_id,
            "username": self.username,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class PasswordHistory(Base):
    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=_utcnow, nullable=False)
    password_masked = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)
    entropy = Column(String(64), nullable=False)
    crack_time = Column(String(128), nullable=False)
    breach_count = Column(Integer, nullable=True)
    strength_label = Column(String(32), nullable=False)
    analysis_json = Column(Text, nullable=False)

    user = relationship("User", back_populates="password_history")

    __table_args__ = (Index("idx_password_history_user", "user_id", "timestamp"),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "password_masked": self.password_masked,
            "score": self.score,
            "entropy": self.entropy,
            "crack_time": self.crack_time,
            "breach_count": self.breach_count,
            "strength_label": self.strength_label,
            "analysis": json.loads(self.analysis_json) if self.analysis_json else {},
        }


class VaultEntry(Base):
    __tablename__ = "vault_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    username_encrypted = Column(Text, nullable=True)
    password_encrypted = Column(Text, nullable=False)
    url_encrypted = Column(Text, nullable=True)
    notes_encrypted = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    user = relationship("User", back_populates="vault_entries")

    def to_dict(self, decrypted=None):
        result = {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if decrypted:
            result.update(decrypted)
        return result


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=_utcnow, nullable=False)
    action = Column(String(128), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)

    user = relationship("User", back_populates="activity_logs")

    __table_args__ = (Index("idx_activity_logs_user", "user_id", "timestamp"),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "action": self.action,
            "details": self.details,
            "ip_address": self.ip_address,
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=_utcnow, nullable=False)
    event_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=True)
    severity = Column(String(16), default="info", nullable=False)

    __table_args__ = (Index("idx_audit_logs_timestamp", "timestamp"),)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "description": self.description,
            "user_id": self.user_id,
            "severity": self.severity,
        }
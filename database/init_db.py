"""Database initialization utilities."""
import logging
from database.connection import get_engine, get_session_factory, init_database
from models.models import User
from security.hashing import hash_password_bcrypt
from config import settings

logger = logging.getLogger(__name__)


def ensure_admin_user():
    """Create a default admin user if no users exist."""
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        if session.query(User).count() == 0:
            admin = User(
                username=settings.default_admin_username,
                password_hash=hash_password_bcrypt(settings.default_admin_password),
                is_admin=True,
                is_active=True,
            )
            session.add(admin)
            session.commit()
            logger.info("Default admin user created: %s", admin.username)
    except Exception as e:
        session.rollback()
        logger.error("Failed to create admin user: %s", e)
        raise
    finally:
        session.close()


def setup_database():
    """Initialize database tables and ensure admin user exists."""
    init_database()
    ensure_admin_user()
    logger.info("Database setup complete.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    setup_database()
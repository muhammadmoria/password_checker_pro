"""Database connection management using SQLAlchemy."""
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Safely import declarative_base for both SQLAlchemy 1.4 and 2.0+
try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base

from config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine = None
_SessionFactory = None


def get_engine():
    """Return the singleton SQLAlchemy engine."""
    global _engine
    if _engine is None:
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
            
        _engine = create_engine(
            settings.database_url,
            connect_args=connect_args,
            echo=False,
            pool_pre_ping=True,
        )

        # Enable SQLite foreign keys and WAL mode
        if settings.database_url.startswith("sqlite"):
            @event.listens_for(_engine, "connect")
            def _set_sqlite_pragma(dbapi_conn, _):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        logger.info("Database engine created: %s", settings.database_url)
    return _engine


def get_session_factory():
    """Return the singleton session factory."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SessionFactory


def init_database():
    """Create all database tables if they do not exist."""
    # Import here to avoid circular imports
    from models.models import Base as ModelBase
    ModelBase.metadata.create_all(get_engine())
    logger.info("Database tables ensured.")
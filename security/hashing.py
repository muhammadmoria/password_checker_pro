"""Password hashing utilities."""
import hashlib
import bcrypt
import os
import logging

logger = logging.getLogger(__name__)


def sha1_hash(password: str) -> str:
    """Return the uppercase SHA-1 hex digest of *password*."""
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def hash_password_bcrypt(password: str) -> str:
    """Hash *password* using bcrypt with a random salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password_bcrypt(password: str, hashed: str) -> bool:
    """Verify *password* against a bcrypt *hashed* string."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError) as e:
        logger.warning("Password verification error: %s", e)
        return False


def generate_salt(length: int = 32) -> str:
    """Generate a cryptographically secure random salt."""
    return os.urandom(length).hex()
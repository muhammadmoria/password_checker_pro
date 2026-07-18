"""Common password detection using a built-in dataset."""
import logging
from pathlib import Path
from config import settings

logger = logging.getLogger(__name__)

_common_passwords: set[str] | None = None
_password_file: Path = settings.assets_dir / "common_passwords.txt"


def load_common_passwords() -> set[str]:
    """Load common passwords from the data file into a set."""
    global _common_passwords
    if _common_passwords is not None:
        return _common_passwords

    _common_passwords = set()
    if _password_file.exists():
        try:
            with open(_password_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    pw = line.strip().lower()
                    if pw:
                        _common_passwords.add(pw)
            logger.info("Loaded %d common passwords.", len(_common_passwords))
        except OSError as e:
            logger.error("Failed to load common passwords file: %s", e)
    else:
        logger.warning("Common passwords file not found: %s", _password_file)

    # Fallback built-in set
    fallback = {
        "password", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
        "letmein", "trustno1", "dragon", "baseball", "111111", "iloveyou", "master",
        "sunshine", "ashley", "bailey", "passw0rd", "shadow", "123123", "654321",
        "superman", "qazwsx", "michael", "football", "password1", "password123",
        "admin", "welcome", "hello", "charlie", "donald", "login", "starwars",
        "121212", "flower", "qwerty123", "1q2w3e4r", "1234567890", "woody",
    }
    _common_passwords.update(fallback)
    return _common_passwords


def is_common_password(password: str) -> bool:
    """Check if *password* appears in the common passwords dataset."""
    pw_set = load_common_passwords()
    return password.lower() in pw_set


def get_common_password_count() -> int:
    """Return the number of common passwords loaded."""
    return len(load_common_passwords())
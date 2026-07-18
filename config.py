"""Application configuration module."""
import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"


def _ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)


_ensure_dirs()


@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from environment."""

    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/password_checker.db")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))

    hibp_api_base: str = os.getenv("HIBP_API_BASE", "https://api.pwnedpasswords.com/range")
    hibp_api_timeout: int = int(os.getenv("HIBP_API_TIMEOUT", "10"))
    hibp_retry_attempts: int = int(os.getenv("HIBP_RETRY_ATTEMPTS", "3"))
    hibp_retry_delay: float = float(os.getenv("HIBP_RETRY_DELAY", "2"))

    pbkdf2_iterations: int = int(os.getenv("PBKDF2_ITERATIONS", "600000"))
    pbkdf2_salt_size: int = int(os.getenv("PBKDF2_SALT_SIZE", "32"))

    default_admin_username: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_admin_password: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMeImmediately123!")

    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    project_root: Path = field(default_factory=lambda: PROJECT_ROOT)
    data_dir: Path = field(default_factory=lambda: DATA_DIR)
    assets_dir: Path = field(default_factory=lambda: ASSETS_DIR)


settings = Settings()
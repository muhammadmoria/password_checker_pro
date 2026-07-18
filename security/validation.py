"""Input validation and sanitization utilities."""
import re
import html

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,128}$")


def validate_username(username: str) -> tuple[bool, str]:
    """Validate a username. Returns (is_valid, message)."""
    if not username or not username.strip():
        return False, "Username must not be empty."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 128:
        return False, "Username must not exceed 128 characters."
    if not USERNAME_PATTERN.match(username):
        return False, "Username may only contain letters, digits, hyphens, and underscores."
    return True, "Valid username."


def sanitize_input(text: str, max_length: int = 4096) -> str:
    """Sanitize input by trimming, escaping HTML, and limiting length."""
    if text is None:
        return ""
    text = str(text).strip()
    if len(text) > max_length:
        text = text[:max_length]
    return html.escape(text, quote=False)


def validate_password_length(password: str, min_length: int = 1) -> tuple[bool, str]:
    if not password:
        return False, "Password must not be empty."
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters."
    return True, "Valid."
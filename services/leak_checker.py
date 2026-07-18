"""Have I Been Pwned password leak checker using k-anonymity."""
import time
import logging
import requests
from security.hashing import sha1_hash
from config import settings

logger = logging.getLogger(__name__)


class LeakCheckResult:
    def __init__(self, breach_count: int, error: str | None = None):
        self.breach_count = breach_count
        self.error = error
        self.is_leaked = breach_count > 0

    @property
    def risk_level(self) -> str:
        if self.error:
            return "Unknown"
        if self.breach_count == 0:
            return "Safe"
        if self.breach_count < 10:
            return "Low Risk"
        if self.breach_count < 100:
            return "Medium Risk"
        if self.breach_count < 1000:
            return "High Risk"
        return "Critical Risk"

    @property
    def risk_color(self) -> str:
        if self.error:
            return "#6b7280"
        if self.breach_count == 0:
            return "#10b981"
        if self.breach_count < 10:
            return "#f59e0b"
        if self.breach_count < 100:
            return "#f97316"
        if self.breach_count < 1000:
            return "#ef4444"
        return "#dc2626"

    def to_dict(self) -> dict:
        return {
            "breach_count": self.breach_count,
            "is_leaked": self.is_leaked,
            "risk_level": self.risk_level,
            "error": self.error,
        }


class LeakChecker:
    """Check passwords against the Have I Been Pwned database using k-anonymity."""

    def __init__(self):
        self.api_base = settings.hibp_api_base
        self.timeout = settings.hibp_api_timeout
        self.retry_attempts = settings.hibp_retry_attempts
        self.retry_delay = settings.hibp_retry_delay

    def check_password(self, password: str) -> LeakCheckResult:
        """Check if *password* has been leaked. Never sends the plaintext password."""
        if not password:
            return LeakCheckResult(0, error="Empty password.")

        full_hash = sha1_hash(password)
        prefix = full_hash[:5]
        suffix = full_hash[5:]

        try:
            hash_list = self._fetch_range(prefix)
            if hash_list is None:
                return LeakCheckResult(0, error="Unable to reach breach database.")

            count = self._match_suffix(suffix, hash_list)
            return LeakCheckResult(count)

        except requests.exceptions.Timeout:
            logger.error("HIBP API timeout.")
            return LeakCheckResult(0, error="Request timed out. Please try again later.")
        except requests.exceptions.ConnectionError:
            logger.error("HIBP API connection error.")
            return LeakCheckResult(0, error="Cannot connect to breach database. Check your network.")
        except Exception as e:
            logger.error("Unexpected error during leak check: %s", e)
            return LeakCheckResult(0, error=f"Unexpected error: {e}")

    def _fetch_range(self, prefix: str) -> dict[str, int] | None:
        """Fetch the list of hash suffixes for a given 5-char prefix."""
        url = f"{self.api_base}/{prefix}"
        headers = {
            "User-Agent": "PasswordCheckerPro/1.0",
            "Add-Padding": "true",
        }

        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                if response.status_code == 200:
                    return self._parse_response(response.text)
                if response.status_code == 429:
                    wait = self.retry_delay * (attempt + 1) * 2
                    logger.warning("Rate limited by HIBP API. Waiting %.1fs.", wait)
                    time.sleep(wait)
                    continue
                logger.error("HIBP API returned status %d.", response.status_code)
                return None
            except requests.exceptions.Timeout:
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise
            except requests.exceptions.ConnectionError:
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise
        return None

    @staticmethod
    def _parse_response(text: str) -> dict[str, int]:
        """Parse the HIBP API response into a dict of suffix -> count."""
        result: dict[str, int] = {}
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            if len(parts) == 2:
                suffix = parts[0].strip().upper()
                try:
                    count = int(parts[1].strip())
                except ValueError:
                    continue
                result[suffix] = count
        return result

    @staticmethod
    def _match_suffix(suffix: str, hash_list: dict[str, int]) -> int:
        """Return the breach count for *suffix* or 0 if not found."""
        return hash_list.get(suffix.upper(), 0)
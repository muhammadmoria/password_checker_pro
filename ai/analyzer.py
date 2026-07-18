"""AI-powered password strength analyzer."""
import re
import math
import string
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any

from security.common_passwords import is_common_password

logger = logging.getLogger(__name__)

LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = string.punctuation
ALL_CHARS = LOWERCASE + UPPERCASE + DIGITS + SYMBOLS

KEYBOARD_ROWS = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "1234567890",
    "qwertyuiopasdfghjklzxcvbnm",
]

COMMON_SEQUENCES = [
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "9876543210",
]

DATE_PATTERNS = [
    re.compile(r"\b(19|20)\d{2}\b"),
    re.compile(r"\b\d{1,2}[/-]\d{1,2}([/-]\d{2,4})?\b"),
]

COMMON_NAMES = [
    "john", "mary", "james", "jennifer", "michael", "sarah", "david", "lisa",
    "robert", "emma", "william", "olivia", "richard", "sophia", "thomas", "ava",
    "charles", "isabella", "daniel", "mia", "matthew", "charlotte", "anthony",
    "amelia", "mark", "harper", "donald", "evelyn", "steven", "abigail",
]

DICTIONARY_WORDS = [
    "password", "admin", "welcome", "login", "user", "guest", "root",
    "love", "baby", "angel", "money", "freedom", "happy", "legend",
    "ninja", "gamer", "shadow", "dark", "light", "fire", "water",
    "earth", "wind", "star", "moon", "sun", "sky", "cloud", "storm",
    "thunder", "lightning", "rain", "snow", "ice", "ocean", "river",
    "mountain", "forest", "desert", "valley", "city", "town", "home",
    "house", "door", "window", "car", "truck", "plane", "train",
    "boat", "ship", "bike", "phone", "computer", "laptop", "tablet",
    "mouse", "keyboard", "screen", "camera", "book", "pen", "pencil",
    "table", "chair", "bed", "lamp", "clock", "watch", "glasses",
    "shirt", "pants", "shoes", "hat", "coat", "dress", "skirt",
    "dog", "cat", "bird", "fish", "horse", "cow", "pig", "sheep",
    "chicken", "duck", "rabbit", "mouse", "bear", "lion", "tiger",
    "wolf", "fox", "deer", "monkey", "snake", "frog", "turtle",
    "red", "blue", "green", "yellow", "orange", "purple", "pink",
    "black", "white", "brown", "gray", "silver", "gold",
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "first", "second", "third", "last", "new", "old",
    "good", "bad", "big", "small", "fast", "slow", "hot", "cold",
    "win", "lose", "play", "stop", "go", "run", "walk", "jump",
    "swim", "fly", "eat", "drink", "sleep", "wake", "dream", "think",
]


@dataclass
class AnalysisResult:
    password_masked: str = ""
    length: int = 0
    entropy_bits: float = 0.0
    charset_size: int = 0
    has_lowercase: bool = False
    has_uppercase: bool = False
    has_digits: bool = False
    has_symbols: bool = False
    score: int = 0
    strength_label: str = "Very Weak"
    crack_time: str = "instant"
    crack_time_seconds: float = 0.0
    is_common_password: bool = False
    has_keyboard_pattern: bool = False
    has_sequential_chars: bool = False
    has_repeated_chars: bool = False
    has_dictionary_word: bool = False
    has_date_pattern: bool = False
    has_personal_info: bool = False
    pattern_findings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    character_diversity: float = 0.0
    zxcvbn_score: int | None = None
    analyzed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PasswordAnalyzer:
    """Comprehensive password strength analyzer."""

    GUESSES_PER_SECOND = 10_000_000_000  # 10 billion guesses/sec (modern GPU)

    def analyze(self, password: str, personal_info: dict[str, str] | None = None) -> AnalysisResult:
        if not password:
            return AnalysisResult()

        result = AnalysisResult()
        result.password_masked = self._mask_password(password)
        result.length = len(password)
        result.analyzed_at = datetime.now().isoformat()

        charset = self._get_charset(password)
        result.charset_size = charset
        result.has_lowercase = any(c in LOWERCASE for c in password)
        result.has_uppercase = any(c in UPPERCASE for c in password)
        result.has_digits = any(c in DIGITS for c in password)
        result.has_symbols = any(c in SYMBOLS for c in password)
        result.character_diversity = len(set(password.lower())) / max(len(password), 1)

        result.entropy_bits = self._calculate_entropy(password, charset)
        result.crack_time_seconds = self._estimate_crack_seconds(result.entropy_bits)
        result.crack_time = self._format_crack_time(result.crack_time_seconds)

        result.is_common_password = is_common_password(password)
        if result.is_common_password:
            result.pattern_findings.append("Password found in common password databases.")

        result.has_keyboard_pattern = self._detect_keyboard_pattern(password)
        if result.has_keyboard_pattern:
            result.pattern_findings.append("Contains keyboard layout patterns (e.g., qwerty, asdf).")

        result.has_sequential_chars = self._detect_sequential(password)
        if result.has_sequential_chars:
            result.pattern_findings.append("Contains sequential characters (e.g., abc, 123).")

        result.has_repeated_chars = self._detect_repeated(password)
        if result.has_repeated_chars:
            result.pattern_findings.append("Contains repeated characters (e.g., aaa, 111).")

        result.has_dictionary_word = self._detect_dictionary(password)
        if result.has_dictionary_word:
            result.pattern_findings.append("Contains common dictionary words.")

        result.has_date_pattern = self._detect_date(password)
        if result.has_date_pattern:
            result.pattern_findings.append("Contains date-like patterns (e.g., 1990, 12/25).")

        if personal_info:
            result.has_personal_info = self._detect_personal_info(password, personal_info)
            if result.has_personal_info:
                result.pattern_findings.append("Contains personal information (name, birthdate, etc.).")

        result.zxcvbn_score = self._get_zxcvbn_score(password)

        result.score = self._calculate_score(password, result)
        result.strength_label = self._score_to_label(result.score)
        result.suggestions = self._generate_suggestions(result)

        return result

    @staticmethod
    def _mask_password(password: str) -> str:
        if len(password) <= 2:
            return "*" * len(password)
        return password[0] + "*" * (len(password) - 2) + password[-1]

    @staticmethod
    def _get_charset(password: str) -> int:
        size = 0
        if any(c in LOWERCASE for c in password):
            size += 26
        if any(c in UPPERCASE for c in password):
            size += 26
        if any(c in DIGITS for c in password):
            size += 10
        if any(c in SYMBOLS for c in password):
            size += len(SYMBOLS)
        if any(c.isspace() for c in password):
            size += 1
        return max(size, 1)

    @staticmethod
    def _calculate_entropy(password: str, charset_size: int) -> float:
        if not password or charset_size == 0:
            return 0.0
        return len(password) * math.log2(charset_size)

    @classmethod
    def _estimate_crack_seconds(cls, entropy_bits: float) -> float:
        if entropy_bits <= 0:
            return 0.0
        total_combinations = 2 ** entropy_bits
        return total_combinations / (2 * cls.GUESSES_PER_SECOND)

    @staticmethod
    def _format_crack_time(seconds: float) -> str:
        if seconds < 1:
            return "instant"
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        if seconds < 3600:
            return f"{seconds / 60:.0f} minutes"
        if seconds < 86400:
            return f"{seconds / 3600:.1f} hours"
        if seconds < 2592000:
            return f"{seconds / 86400:.1f} days"
        if seconds < 31536000:
            return f"{seconds / 2592000:.1f} months"
        years = seconds / 31536000
        if years < 1000:
            return f"{years:.1f} years"
        if years < 1_000_000:
            return f"{years / 1000:.1f} thousand years"
        if years < 1_000_000_000:
            return f"{years / 1_000_000:.1f} million years"
        if years < 1_000_000_000_000:
            return f"{years / 1_000_000_000:.1f} billion years"
        return f"{years / 1_000_000_000_000:.1f} trillion years"

    @staticmethod
    def _detect_keyboard_pattern(password: str) -> bool:
        pw_lower = password.lower()
        for row in KEYBOARD_ROWS:
            for i in range(len(row) - 2):
                substr = row[i:i + 3]
                if substr in pw_lower:
                    return True
                if substr[::-1] in pw_lower:
                    return True
        # Check shifted keyboard patterns
        shifted = "!@#$%^&*()"
        digits = "1234567890"
        for i in range(len(shifted) - 2):
            substr = shifted[i:i + 3]
            if substr in password:
                return True
        return False

    @staticmethod
    def _detect_sequential(password: str) -> bool:
        pw_lower = password.lower()
        for seq in COMMON_SEQUENCES:
            for i in range(len(seq) - 2):
                substr = seq[i:i + 3]
                if substr in pw_lower:
                    return True
                if substr[::-1] in pw_lower:
                    return True
        # Check for 3+ consecutive ascending/descending characters
        for i in range(len(password) - 2):
            a, b, c = ord(password[i]), ord(password[i + 1]), ord(password[i + 2])
            if b == a + 1 and c == b + 1:
                return True
            if b == a - 1 and c == b - 1:
                return True
        return False

    @staticmethod
    def _detect_repeated(password: str) -> bool:
        if len(password) < 3:
            return False
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                return True
        # Check repeated substrings (e.g., abcabc)
        for length in range(2, len(password) // 2 + 1):
            for i in range(len(password) - length * 2 + 1):
                substr = password[i:i + length]
                if substr == password[i + length:i + length * 2]:
                    return True
        return False

    @staticmethod
    def _detect_dictionary(password: str) -> bool:
        pw_lower = password.lower()
        for word in DICTIONARY_WORDS:
            if len(word) >= 4 and word in pw_lower:
                return True
        for name in COMMON_NAMES:
            if name in pw_lower:
                return True
        return False

    @staticmethod
    def _detect_date(password: str) -> bool:
        for pattern in DATE_PATTERNS:
            if pattern.search(password):
                return True
        return False

    @staticmethod
    def _detect_personal_info(password: str, personal_info: dict[str, str]) -> bool:
        pw_lower = password.lower()
        for key, value in personal_info.items():
            if value and len(str(value)) >= 3:
                if str(value).lower() in pw_lower:
                    return True
        return False

    @staticmethod
    def _get_zxcvbn_score(password: str) -> int | None:
        try:
            from zxcvbn import zxcvbn
            result = zxcvbn(password)
            return result.get("score", None)
        except Exception:
            return None

    @classmethod
    def _calculate_score(cls, password: str, result: AnalysisResult) -> int:
        if result.is_common_password:
            return max(5, min(15, result.zxcvbn_score * 5 if result.zxcvbn_score is not None else 10))

        entropy_score = min(result.entropy_bits / 128 * 100, 100)
        length_score = min(result.length / 20 * 100, 100)
        diversity_score = min(result.character_diversity * 100, 100)
        charset_score = min(result.charset_size / 95 * 100, 100)

        raw = (
            entropy_score * 0.35
            + length_score * 0.20
            + charset_score * 0.20
            + diversity_score * 0.10
        )

        if result.zxcvbn_score is not None:
            zxcvbn_contribution = result.zxcvbn_score * 25
            raw = raw * 0.7 + zxcvbn_contribution * 0.3

        penalty = 0
        if result.has_keyboard_pattern:
            penalty += 20
        if result.has_sequential_chars:
            penalty += 15
        if result.has_repeated_chars:
            penalty += 15
        if result.has_dictionary_word:
            penalty += 20
        if result.has_date_pattern:
            penalty += 10
        if result.has_personal_info:
            penalty += 25

        score = max(0, min(100, int(raw - penalty)))

        if result.length < 8:
            score = min(score, 30)
        elif result.length < 12:
            score = min(score, 60)

        return score

    @staticmethod
    def _score_to_label(score: int) -> str:
        if score < 20:
            return "Very Weak"
        if score < 40:
            return "Weak"
        if score < 60:
            return "Fair"
        if score < 75:
            return "Good"
        if score < 90:
            return "Strong"
        return "Very Strong"

    @staticmethod
    def _generate_suggestions(result: AnalysisResult) -> list[str]:
        suggestions = []
        if result.length < 12:
            suggestions.append("Increase length to at least 12 characters for better security.")
        if not result.has_uppercase:
            suggestions.append("Add uppercase letters (A-Z).")
        if not result.has_lowercase:
            suggestions.append("Add lowercase letters (a-z).")
        if not result.has_digits:
            suggestions.append("Include numbers (0-9).")
        if not result.has_symbols:
            suggestions.append("Add special characters (!@#$%^&*).")
        if result.is_common_password:
            suggestions.append("This password is in known breach databases. Change it immediately.")
        if result.has_keyboard_pattern:
            suggestions.append("Avoid keyboard patterns like 'qwerty' or 'asdf'.")
        if result.has_sequential_chars:
            suggestions.append("Avoid sequential characters like '123' or 'abc'.")
        if result.has_repeated_chars:
            suggestions.append("Avoid repeated characters like 'aaa' or '111'.")
        if result.has_dictionary_word:
            suggestions.append("Replace dictionary words with unrelated characters or use a passphrase.")
        if result.has_date_pattern:
            suggestions.append("Remove dates that could be personally identifiable.")
        if result.has_personal_info:
            suggestions.append("Do not include personal information in your password.")
        if result.character_diversity < 0.5:
            suggestions.append("Use a wider variety of unique characters.")
        if not suggestions:
            suggestions.append("Excellent password! Consider using a password manager to store it safely.")
        return suggestions
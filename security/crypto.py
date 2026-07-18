"""AES encryption manager using Fernet (AES-128-CBC + HMAC-SHA256)."""
import base64
import hashlib
import logging
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import settings

logger = logging.getLogger(__name__)


class CryptoManager:
    """Encrypt and decrypt strings using a password-derived Fernet key."""

    def __init__(self, password: str, salt: bytes | None = None):
        if not password:
            raise ValueError("Password must not be empty.")
        self._salt = salt if salt is not None else os_urandom(settings.pbkdf2_salt_size)
        self._key = self._derive_key(password, self._salt)
        self._fernet = Fernet(self._key)

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=settings.pbkdf2_iterations,
        )
        key = kdf.derive(password.encode("utf-8"))
        return base64.urlsafe_b64encode(key)

    @property
    def salt(self) -> bytes:
        return self._salt

    @property
    def salt_hex(self) -> str:
        return self._salt.hex()

    def encrypt(self, plaintext: str) -> str:
        if plaintext is None:
            return ""
        token = self._fernet.encrypt(plaintext.encode("utf-8"))
        return token.decode("utf-8")

    def decrypt(self, token: str) -> str:
        if not token:
            return ""
        try:
            return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            logger.error("Decryption failed: invalid token or wrong key.")
            raise ValueError("Decryption failed: invalid key or corrupted data.")

    @staticmethod
    def generate_key() -> bytes:
        return Fernet.generate_key()


def os_urandom(n: int) -> bytes:
    import os
    return os.urandom(n)
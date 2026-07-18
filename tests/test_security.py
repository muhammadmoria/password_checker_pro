"""Tests for security modules."""
import pytest
from security.hashing import sha1_hash, hash_password_bcrypt, verify_password_bcrypt, generate_salt
from security.crypto import CryptoManager
from security.validation import validate_username, sanitize_input, validate_password_length
from security.common_passwords import is_common_password, load_common_passwords


class TestHashing:
    def test_sha1_consistency(self):
        assert sha1_hash("test") == sha1_hash("test")

    def test_sha1_different_inputs(self):
        assert sha1_hash("test1") != sha1_hash("test2")

    def test_bcrypt_hash_and_verify(self):
        password = "MySecurePassword123!"
        hashed = hash_password_bcrypt(password)
        assert hashed != password
        assert verify_password_bcrypt(password, hashed) is True

    def test_bcrypt_wrong_password(self):
        hashed = hash_password_bcrypt("correct_password")
        assert verify_password_bcrypt("wrong_password", hashed) is False

    def test_bcrypt_hash_format(self):
        hashed = hash_password_bcrypt("test")
        assert hashed.startswith("$2b$")

    def test_generate_salt_length(self):
        salt = generate_salt(32)
        assert len(salt) == 64  # hex string is 2x byte length

    def test_generate_salt_unique(self):
        salt1 = generate_salt(16)
        salt2 = generate_salt(16)
        assert salt1 != salt2


class TestCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        crypto = CryptoManager("my_password")
        plaintext = "Secret data to encrypt"
        encrypted = crypto.encrypt(plaintext)
        assert encrypted != plaintext
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_empty_string(self):
        crypto = CryptoManager("password")
        assert crypto.encrypt("") == ""
        assert crypto.decrypt("") == ""

    def test_decrypt_with_wrong_password(self):
        crypto1 = CryptoManager("correct_password")
        encrypted = crypto1.encrypt("secret data")

        crypto2 = CryptoManager("wrong_password", salt=crypto1.salt)
        with pytest.raises(ValueError):
            crypto2.decrypt(encrypted)

    def test_same_password_different_salt(self):
        crypto1 = CryptoManager("password")
        crypto2 = CryptoManager("password")
        assert crypto1.salt != crypto2.salt

    def test_salt_hex_property(self):
        crypto = CryptoManager("password")
        assert isinstance(crypto.salt_hex, str)
        assert len(crypto.salt_hex) > 0

    def test_empty_password_raises(self):
        with pytest.raises(ValueError):
            CryptoManager("")


class TestValidation:
    def test_valid_username(self):
        ok, msg = validate_username("john_doe")
        assert ok is True

    def test_short_username(self):
        ok, msg = validate_username("ab")
        assert ok is False
        assert "3 characters" in msg

    def test_empty_username(self):
        ok, msg = validate_username("")
        assert ok is False

    def test_invalid_chars_username(self):
        ok, msg = validate_username("user@name")
        assert ok is False

    def test_sanitize_removes_html(self):
        result = sanitize_input("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_sanitize_truncates(self):
        result = sanitize_input("a" * 10000, max_length=100)
        assert len(result) <= 100

    def test_sanitize_none(self):
        assert sanitize_input(None) == ""

    def test_password_length_valid(self):
        ok, msg = validate_password_length("12345678", min_length=8)
        assert ok is True

    def test_password_length_too_short(self):
        ok, msg = validate_password_length("1234", min_length=8)
        assert ok is False


class TestCommonPasswords:
    def test_common_password_detected(self):
        assert is_common_password("password") is True

    def test_common_password_case_insensitive(self):
        assert is_common_password("PASSWORD") is True

    def test_unique_password_not_detected(self):
        assert is_common_password("X7#kQ9!mL2$pR5&") is False

    def test_load_returns_set(self):
        pw_set = load_common_passwords()
        assert isinstance(pw_set, set)
        assert len(pw_set) > 0
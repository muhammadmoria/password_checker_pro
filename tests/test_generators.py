"""Tests for the password and passphrase generators."""
import string
import pytest
from services.generator_service import GeneratorService


@pytest.fixture
def gen():
    return GeneratorService()


class TestPasswordGenerator:
    def test_default_length(self, gen):
        pw = gen.generate_password(16)
        assert len(pw) == 16

    def test_custom_length(self, gen):
        pw = gen.generate_password(32)
        assert len(pw) == 32

    def test_minimum_length_enforced(self, gen):
        pw = gen.generate_password(2)
        assert len(pw) == 4

    def test_maximum_length_enforced(self, gen):
        pw = gen.generate_password(200)
        assert len(pw) == 128

    def test_only_lowercase(self, gen):
        pw = gen.generate_password(20, use_uppercase=False, use_digits=False, use_symbols=False)
        assert all(c in string.ascii_lowercase for c in pw)

    def test_only_digits(self, gen):
        pw = gen.generate_password(20, use_uppercase=False, use_lowercase=False, use_symbols=False)
        assert all(c in string.digits for c in pw)

    def test_all_character_types_present(self, gen):
        pw = gen.generate_password(50, True, True, True, True)
        assert any(c in string.ascii_lowercase for c in pw)
        assert any(c in string.ascii_uppercase for c in pw)
        assert any(c in string.digits for c in pw)
        assert any(c in string.punctuation for c in pw)

    def test_exclude_similar(self, gen):
        pw = gen.generate_password(50, True, True, True, True, exclude_similar=True)
        similar = "il1Lo0O"
        assert not any(c in similar for c in pw)

    def test_no_pools_selected(self, gen):
        pw = gen.generate_password(10, False, False, False, False)
        assert len(pw) == 10

    def test_uniqueness(self, gen):
        passwords = {gen.generate_password(20) for _ in range(100)}
        assert len(passwords) == 100


class TestPassphraseGenerator:
    def test_default_passphrase(self, gen):
        pp = gen.generate_passphrase(4)
        assert len(pp) > 0

    def test_word_count(self, gen):
        pp = gen.generate_passphrase(4, separator="-", capitalize=False, add_number=False, add_symbol=False)
        assert len(pp.split("-")) == 4

    def test_custom_separator(self, gen):
        pp = gen.generate_passphrase(3, separator="_", capitalize=False, add_number=False, add_symbol=False)
        assert "_" in pp

    def test_capitalize(self, gen):
        pp = gen.generate_passphrase(3, capitalize=True, add_number=False, add_symbol=False)
        words = pp.split("-")
        assert any(w[0].isupper() for w in words)

    def test_add_number(self, gen):
        pp = gen.generate_passphrase(3, add_number=True, add_symbol=False)
        assert any(c.isdigit() for c in pp)

    def test_add_symbol(self, gen):
        pp = gen.generate_passphrase(3, add_number=False, add_symbol=True)
        assert any(c in string.punctuation for c in pp)

    def test_minimum_words(self, gen):
        pp = gen.generate_passphrase(1)
        assert len(pp.split("-")) >= 2

    def test_maximum_words(self, gen):
        pp = gen.generate_passphrase(20, separator="-", capitalize=False, add_number=False, add_symbol=False)
        assert len(pp.split("-")) <= 12


class TestPinGenerator:
    def test_default_pin(self, gen):
        pin = gen.generate_pin(6)
        assert len(pin) == 6

    def test_all_digits(self, gen):
        pin = gen.generate_pin(8)
        assert all(c in string.digits for c in pin)

    def test_minimum_length(self, gen):
        pin = gen.generate_pin(2)
        assert len(pin) == 4

    def test_maximum_length(self, gen):
        pin = gen.generate_pin(20)
        assert len(pin) == 12

    def test_uniqueness(self, gen):
        pins = {gen.generate_pin(6) for _ in range(50)}
        assert len(pins) == 50
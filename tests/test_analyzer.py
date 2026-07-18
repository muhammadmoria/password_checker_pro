"""Tests for the AI password analyzer."""
import pytest
from ai.analyzer import PasswordAnalyzer


@pytest.fixture
def analyzer():
    return PasswordAnalyzer()


class TestEntropy:
    def test_empty_password(self, analyzer):
        result = analyzer.analyze("")
        assert result.entropy_bits == 0.0
        assert result.score == 0

    def test_simple_password_low_entropy(self, analyzer):
        result = analyzer.analyze("abc")
        assert result.entropy_bits < 20

    def test_complex_password_high_entropy(self, analyzer):
        result = analyzer.analyze("X7#kQ9!mL2$pR5&")
        assert result.entropy_bits > 80

    def test_entropy_increases_with_length(self, analyzer):
        short = analyzer.analyze("Abc123!")
        long = analyzer.analyze("Abc123!Abc123!Abc123!")
        assert long.entropy_bits > short.entropy_bits


class TestPatternDetection:
    def test_keyboard_pattern_detected(self, analyzer):
        result = analyzer.analyze("qwerty123")
        assert result.has_keyboard_pattern is True

    def test_keyboard_pattern_not_detected(self, analyzer):
        result = analyzer.analyze("X7#kQ9!mL2$")
        assert result.has_keyboard_pattern is False

    def test_sequential_chars_detected(self, analyzer):
        result = analyzer.analyze("abcdef123")
        assert result.has_sequential_chars is True

    def test_repeated_chars_detected(self, analyzer):
        result = analyzer.analyze("aaabbbccc")
        assert result.has_repeated_chars is True

    def test_dictionary_word_detected(self, analyzer):
        result = analyzer.analyze("password123")
        assert result.has_dictionary_word is True

    def test_date_pattern_detected(self, analyzer):
        result = analyzer.analyze("password1990")
        assert result.has_date_pattern is True


class TestScoring:
    def test_common_password_low_score(self, analyzer):
        result = analyzer.analyze("password")
        assert result.score < 20

    def test_common_password_low_score_2(self, analyzer):
        result = analyzer.analyze("123456")
        assert result.score < 20

    def test_strong_password_high_score(self, analyzer):
        result = analyzer.analyze("Kx9#mQ2!vR7$pL4@")
        assert result.score >= 75

    def test_short_password_capped(self, analyzer):
        result = analyzer.analyze("Ab1!")
        assert result.score <= 30

    def test_score_in_range(self, analyzer):
        result = analyzer.analyze("MyP@ssw0rd")
        assert 0 <= result.score <= 100


class TestCrackTime:
    def test_weak_password_fast_crack(self, analyzer):
        result = analyzer.analyze("abc")
        assert "instant" in result.crack_time or "second" in result.crack_time

    def test_strong_password_slow_crack(self, analyzer):
        result = analyzer.analyze("Kx9#mQ2!vR7$pL4@nB8&yT3")
        assert "year" in result.crack_time


class TestSuggestions:
    def test_suggestions_for_weak_password(self, analyzer):
        result = analyzer.analyze("abc")
        assert len(result.suggestions) > 0

    def test_suggestions_include_length(self, analyzer):
        result = analyzer.analyze("Ab1!")
        assert any("length" in s.lower() for s in result.suggestions)


class TestMasking:
    def test_short_password_masked(self, analyzer):
        result = analyzer.analyze("ab")
        assert result.password_masked == "**"

    def test_long_password_masked(self, analyzer):
        result = analyzer.analyze("password123")
        assert result.password_masked[0] == "p"
        assert result.password_masked[-1] == "3"
        assert "*" in result.password_masked


class TestPersonalInfo:
    def test_personal_info_detected(self, analyzer):
        result = analyzer.analyze("john1990", personal_info={"name": "john"})
        assert result.has_personal_info is True

    def test_no_personal_info(self, analyzer):
        result = analyzer.analyze("X7#kQ9!mL2$", personal_info={"name": "john"})
        assert result.has_personal_info is False
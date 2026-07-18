"""Tests for the leak checker service."""
import pytest
from unittest.mock import patch, MagicMock
from services.leak_checker import LeakChecker, LeakCheckResult
from security.hashing import sha1_hash


@pytest.fixture
def checker():
    return LeakChecker()


class TestSha1Hash:
    def test_known_hash(self):
        assert sha1_hash("password") == "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8"

    def test_empty_string(self):
        assert sha1_hash("") == "DA39A3EE5E6B4B0D3255BFEF95601890AFD80709"

    def test_uppercase_output(self):
        result = sha1_hash("test")
        assert result == result.upper()


class TestLeakCheckResult:
    def test_safe_result(self):
        r = LeakCheckResult(0)
        assert r.is_leaked is False
        assert r.risk_level == "Safe"

    def test_low_risk(self):
        r = LeakCheckResult(5)
        assert r.is_leaked is True
        assert r.risk_level == "Low Risk"

    def test_medium_risk(self):
        r = LeakCheckResult(50)
        assert r.risk_level == "Medium Risk"

    def test_high_risk(self):
        r = LeakCheckResult(500)
        assert r.risk_level == "High Risk"

    def test_critical_risk(self):
        r = LeakCheckResult(5000)
        assert r.risk_level == "Critical Risk"

    def test_error_result(self):
        r = LeakCheckResult(0, error="Network error")
        assert r.risk_level == "Unknown"


class TestParseResponse:
    def test_parse_valid_response(self):
        text = "00AEEF4321:5\n0ABCD1234:10\n0FFF5678:1"
        result = LeakChecker._parse_response(text)
        assert result["00AEEF4321"] == 5
        assert result["0ABCD1234"] == 10
        assert result["0FFF5678"] == 1

    def test_parse_empty_response(self):
        result = LeakChecker._parse_response("")
        assert result == {}

    def test_parse_malformed_line(self):
        text = "VALID:5\nINVALID\nALSO:NOTANUMBER"
        result = LeakChecker._parse_response(text)
        assert result == {"VALID": 5}


class TestMatchSuffix:
    def test_match_found(self):
        hash_list = {"A1B2C3D4E5": 42}
        assert LeakChecker._match_suffix("A1B2C3D4E5", hash_list) == 42

    def test_no_match(self):
        hash_list = {"A1B2C3D4E5": 42}
        assert LeakChecker._match_suffix("ZZZZZZZZZZ", hash_list) == 0


class TestCheckPassword:
    @patch("services.leak_checker.requests.get")
    def test_check_leaked_password(self, mock_get, checker):
        full_hash = sha1_hash("password")
        prefix = full_hash[:5]
        suffix = full_hash[5:]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = f"{suffix}:3523808\nOTHERSUFFIX:5"
        mock_get.return_value = mock_response

        result = checker.check_password("password")
        assert result.breach_count > 0
        assert result.is_leaked is True

    @patch("services.leak_checker.requests.get")
    def test_check_safe_password(self, mock_get, checker):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OTHER1:5\nOTHER2:10"
        mock_get.return_value = mock_response

        result = checker.check_password("Un1queP@ss!9876xyz")
        assert result.breach_count == 0
        assert result.is_leaked is False

    def test_check_empty_password(self, checker):
        result = checker.check_password("")
        assert result.error is not None
        assert result.breach_count == 0

    @patch("services.leak_checker.requests.get")
    def test_api_timeout_handling(self, mock_get, checker):
        import requests as req
        mock_get.side_effect = req.exceptions.Timeout()
        result = checker.check_password("test123")
        assert result.error is not None
        assert "timed out" in result.error.lower()
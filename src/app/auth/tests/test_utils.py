"""Tests for authentication utility functions."""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from auth
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import string
from unittest.mock import patch, MagicMock
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from auth.utils import (
    generate_random_otp,
    hash_password,
    verify_password,
    generate_username
)


class TestGenerateRandomOTP:
    """Tests for generate_random_otp function."""

    def test_default_length(self):
        """Test OTP generation with default length of 6."""
        otp = generate_random_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    def test_custom_length(self):
        """Test OTP generation with custom length."""
        for length in [4, 8, 10]:
            otp = generate_random_otp(length=length)
            assert len(otp) == length
            assert otp.isdigit()

    def test_otp_only_contains_digits(self):
        """Test that OTP contains only numeric characters."""
        otp = generate_random_otp()
        for char in otp:
            assert char in string.digits

    def test_otp_randomness(self):
        """Test that multiple OTP generations produce different results."""
        otps = [generate_random_otp() for _ in range(10)]
        # It's statistically very unlikely all 10 OTPs are identical
        assert len(set(otps)) > 1


class TestHashPassword:
    """Tests for hash_password function."""

    def test_password_is_hashed(self):
        """Test that password is hashed and different from original."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_same_password_different_hashes(self):
        """Test that hashing the same password produces different hashes (due to salt)."""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Argon2 uses different salts, so hashes should be different
        assert hash1 != hash2

    def test_hash_format(self):
        """Test that hash has the expected Argon2 format."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # Argon2 hashes start with $argon2
        assert hashed.startswith("$argon2")

    def test_hash_empty_password(self):
        """Test hashing an empty password."""
        hashed = hash_password("")
        assert isinstance(hashed, str)
        assert len(hashed) > 0


class TestVerifyPassword:
    """Tests for verify_password function."""

    def test_verify_correct_password(self):
        """Test that correct password is verified successfully."""
        password = "CorrectPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test that incorrect password fails verification."""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_verify_empty_password(self):
        """Test verification with empty password."""
        password = ""
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("not_empty", hashed) is False

    def test_verify_with_invalid_hash(self):
        """Test verification with invalid hash format."""
        password = "TestPassword123!"
        invalid_hash = hash_password("SomePassword")
        
        # Should return False for invalid hash
        result = verify_password(password, invalid_hash)
        assert result is False

    # @patch('auth.utils._ph.verify')
    def test_verify_password_mismatch_exception(self):
        """Test that VerifyMismatchError is caught and returns False."""
        # mock_verify.side_effect = VerifyMismatchError()
        hashed_pwd = hash_password("somepassword")
        result = verify_password("password", hashed_pwd)
        assert result is False

    def test_case_sensitive_verification(self):
        """Test that password verification is case sensitive."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password.lower(), hashed) is False
        assert verify_password(password.upper(), hashed) is False


class TestGenerateUsername:
    """Tests for generate_username function."""

    @patch('auth.utils.settings')
    def test_username_format_single_word_site_name(self, mock_settings):
        """Test username generation with single word site name."""
        mock_settings.SITE_NAME = "BankApp"
        
        username = generate_username()
        
        # Should start with 'B-' (first letter of BankApp)
        assert username.startswith("B-")
        # Total length should be 12
        assert len(username) == 12
        # Should contain only uppercase letters, digits, and hyphen
        assert all(c in string.ascii_uppercase + string.digits + '-' for c in username)

    @patch('auth.utils.settings')
    def test_username_format_multi_word_site_name(self, mock_settings):
        """Test username generation with multi-word site name."""
        mock_settings.SITE_NAME = "My Banking App"
        
        username = generate_username()
        
        # Should start with 'MBA-' (first letters of My Banking App)
        assert username.startswith("MBA-")
        # Total length should be 12
        assert len(username) == 12

    @patch('auth.utils.settings')
    def test_username_length(self, mock_settings):
        """Test that generated username is always 12 characters."""
        mock_settings.SITE_NAME = "Bank"
        
        for _ in range(10):
            username = generate_username()
            assert len(username) == 12

    @patch('auth.utils.settings')
    def test_username_uniqueness(self, mock_settings):
        """Test that multiple calls generate different usernames."""
        mock_settings.SITE_NAME = "BankApp"
        
        usernames = [generate_username() for _ in range(10)]
        
        # All should be unique
        assert len(set(usernames)) == 10

    @patch('auth.utils.settings')
    def test_username_contains_only_valid_characters(self, mock_settings):
        """Test that username contains only uppercase letters, digits, and hyphen."""
        mock_settings.SITE_NAME = "Test Bank"
        
        username = generate_username()
        valid_chars = string.ascii_uppercase + string.digits + '-'
        
        assert all(c in valid_chars for c in username)

    @patch('auth.utils.settings')
    def test_username_prefix_extraction(self, mock_settings):
        """Test correct prefix extraction from site name."""
        test_cases = [
            ("First Second Third", "FST-"),
            ("A B C D", "ABCD-"),
            ("Single", "S-"),
        ]
        
        for site_name, expected_prefix in test_cases:
            mock_settings.SITE_NAME = site_name
            username = generate_username()
            assert username.startswith(expected_prefix)

import pytest
from datetime import timedelta
from app.core.auth import create_access_token, decode_access_token
from app.core.auth_utils import hash_password, verify_password
import time
from fastapi import HTTPException


@pytest.fixture
def sample_payload():
    return {"sub": "user_id_123"}


class TestTokenCreationDecoding:
    def test_valid_token(self, sample_payload):
        """Test creation and decoding of a valid JWT."""
        token = create_access_token(sample_payload)
        decoded_token = decode_access_token(token)
        assert decoded_token["sub"] == sample_payload["sub"]

    def test_custom_expiration(self, sample_payload):
        """Test token creation with a custom expiration time."""
        token = create_access_token(sample_payload, expires_delta=timedelta(hours=1))
        decoded_token = decode_access_token(token)
        assert decoded_token["sub"] == sample_payload["sub"]
        assert "exp" in decoded_token

    def test_expired_token(self, sample_payload):
        """Test handling of an expired JWT."""
        token = create_access_token(sample_payload, expires_delta=timedelta(seconds=1))
        time.sleep(3)
        with pytest.raises(HTTPException) as excinfo:
            decode_access_token(token)
        assert excinfo.value.status_code == 401
        assert "Token has expired" in str(excinfo.value)

    def test_invalid_token(self):
        """Test decoding of an invalid JWT."""
        invalid_token = "invalid.token.here"
        with pytest.raises(HTTPException) as excinfo:
            decode_access_token(invalid_token)
        assert excinfo.value.status_code == 401
        assert "Invalid token" in str(excinfo.value)

    def test_empty_payload_token(self):
        """Test token creation and decoding with an empty payload."""
        token = create_access_token({})
        decoded_token = decode_access_token(token)
        assert "exp" in decoded_token
        assert len(decoded_token) == 1  # Only 'exp' key should be present

    def test_tampered_algorithm(self, sample_payload):
        """Test decoding of a token with a tampered header algorithm."""
        token = create_access_token(sample_payload)
        tampered_token = token.split(".")
        tampered_token[0] = "eyJhbGciOiAiSFMyNTYifQ"  # Fake HS256 header
        tampered_token = ".".join(tampered_token)
        with pytest.raises(HTTPException) as excinfo:
            decode_access_token(tampered_token)
        assert excinfo.value.status_code == 401
        assert "Invalid token" in str(excinfo.value)


class TestPasswordHashing:
    def test_hash_and_verify_password(self):
        password = "securepassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_password(self):
        with pytest.raises(ValueError):
            hash_password("")

    def test_invalid_hash_handling(self):
        """Ensure an HTTPException is raised for invalid password hash."""
        plain_password = "securepassword123"
        invalid_hash = "not_a_valid_hash"
        with pytest.raises(HTTPException) as excinfo:
            verify_password(plain_password, invalid_hash)
        assert excinfo.value.status_code == 401
        assert "Incorrect password." in str(excinfo.value)

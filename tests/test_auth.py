import pytest
from datetime import timedelta
from app.core.auth import create_access_token, decode_access_token
from app.core.auth_utils import hash_password, verify_password
import time
from fastapi import HTTPException


# Test valid token creation and decoding
def test_valid_token():
    """
    Test creation and decoding of a valid JWT
    """
    # Sample payload
    data = {"sub": "user_id_123"}

    # Create an access token
    token = create_access_token(data)

    # Decode the token
    decoded_token = decode_access_token(token)

    # Ensure the decoded token matches the original payload
    assert decoded_token["sub"] == "user_id_123"


# Test token with custom expiration
def test_token_custom_expiration():
    """
    Test token creation with a custom expiration time
    """
    # Sample payload
    data = {"sub": "user_id_123"}

    # Create an access token with custom expiration (1 hour)
    token = create_access_token(data, expires_delta=timedelta(hours=1))

    # Decode the token
    decoded_token = decode_access_token(token)

    # Ensure the decoded token matches the original payload
    assert decoded_token["sub"] == "user_id_123"
    assert "exp" in decoded_token  # Ensure expiration is set


# Test expired token handling
def test_decode_expired_access_token():
    """
    Test handling of an expired JWT
    """
    # Sample payload
    data = {"sub": "user_id_123"}

    # Create a token with short expiration (1 second)
    token = create_access_token(data, expires_delta=timedelta(seconds=1))

    # Wait for the token to expire
    time.sleep(3)

    # Try to decode it, expecting an HTTPException due to expiration
    with pytest.raises(HTTPException) as excinfo:
        decode_access_token(token)

    assert excinfo.value.status_code == 401
    assert "Token has expired" in str(excinfo.value)


# Test invalid token handling
def test_decode_invalid_access_token():
    """
    Test decoding of an invalid JWT
    """
    # Invalid token (tampered)
    invalid_token = "invalid.token.here"

    # Try to decode it, expecting an HTTPException due to invalidity
    with pytest.raises(HTTPException) as excinfo:
        decode_access_token(invalid_token)

    assert excinfo.value.status_code == 401
    assert "Invalid token" in str(excinfo.value)


# Test empty payload
def test_empty_payload():
    """
    Test token creation and decoding with an empty payload
    """
    # Create an access token with an empty payload
    data = {}
    token = create_access_token(data)

    # Decode the token and ensure it's empty
    decoded_token = decode_access_token(token)

    assert "exp" in decoded_token
    assert len(decoded_token) == 1  # Only 'exp' key should be present


# Test token with a missing expiration
def test_missing_expiration_in_token():
    """
    Test creation and decoding of a token with no expiration
    """
    # Sample payload
    data = {"sub": "user_id_123"}

    # Create a token without providing an expiration time
    token = create_access_token(data, expires_delta=None)

    # Decode the token and check that no expiration was added
    decoded_token = decode_access_token(token)

    assert decoded_token["sub"] == "user_id_123"
    assert "exp" in decoded_token  # JWT should still include an expiration


# Test invalid algorithm handling (manipulate header)
def test_invalid_algorithm_in_token():
    """
    Test decoding of a token with an invalid algorithm
    """
    # Sample payload
    data = {"sub": "user_id_123"}

    # Create an access token
    token = create_access_token(data)

    # Manually tamper with the header to use an invalid algorithm
    tampered_token = token.split(".")
    tampered_token[0] = "eyJhbGciOiAiSFMyNTYifQ"  # Set algorithm to "HS256"
    tampered_token = ".".join(tampered_token)

    # Try to decode the tampered token, expecting an HTTPException
    with pytest.raises(HTTPException) as excinfo:
        decode_access_token(tampered_token)

    assert excinfo.value.status_code == 401
    assert "Invalid token" in str(excinfo.value)


def test_hash_and_verify_password():
    password = "securepassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_empty_password():
    with pytest.raises(ValueError):
        hash_password("")


def test_verify_password_with_invalid_hash():
    """
    Test that an HTTPException is raised when verify_password is called with an invalid hash.
    """
    plain_password = "securepassword123"
    invalid_hash = "not_a_valid_hash"

    with pytest.raises(HTTPException) as excinfo:
        verify_password(plain_password, invalid_hash)

    assert excinfo.value.status_code == 401
    assert "Incorrect password." in str(excinfo.value)

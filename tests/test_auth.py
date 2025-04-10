import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status
from app.services.jwt_utils import create_access_token, decode_access_token
from app.services.auth_utils import hash_password, verify_password
from app.services.auth import get_current_user
from app.models.user import User
import time


@pytest.fixture
def sample_payload():
    """Fixture to provide a sample payload for token tests."""
    return {"sub": 123}


class TestTokenCreationDecoding:
    async def test_valid_token(self, sample_payload):
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
        time.sleep(2)  # Ensure the token expires
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

    def test_near_expiration_token(self, sample_payload):
        """Test decoding of a token that expires almost immediately."""
        token = create_access_token(
            sample_payload, expires_delta=timedelta(seconds=0.5)
        )
        time.sleep(1)  # Wait until the token has expired
        with pytest.raises(HTTPException) as excinfo:
            decode_access_token(token)
        assert excinfo.value.status_code == 401
        assert "Token has expired" in str(excinfo.value)


class TestPasswordHashing:
    def test_hash_and_verify_password(self):
        """Test that a password can be hashed and verified successfully."""
        password = "securepassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_password(self):
        """Test that hashing an empty password raises a ValueError."""
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

    def test_long_password_hashing(self):
        """Test hashing and verifying a very long password."""
        long_password = "a" * 1000
        hashed = hash_password(long_password)
        assert verify_password(long_password, hashed) is True

    def test_common_edge_cases_in_passwords(self):
        """Test hashing and verifying edge case passwords."""
        edge_cases = ["12345678", "!@#$%^&*()", " " * 8]
        for password in edge_cases:
            hashed = hash_password(password)
            assert verify_password(password, hashed) is True


class TestGetCurrentUser:
    @pytest.mark.asyncio
    @patch("app.services.auth.decode_access_token")
    async def test_get_current_user_success(self, mock_decode_access_token, db_session):
        """Test successful retrieval of current user from token."""
        sample_payload = {"sub": 123}
        mock_decode_access_token.return_value = sample_payload

        # Add a user to the PostgreSQL test database with all required fields
        new_user = User(
            id=123,
            username="testuser",
            email="test@example.com",
            hashed_password="test_hash",  # Add required hashed_password
            is_active=True,
            role="USER",
        )
        db_session.add(new_user)
        await db_session.commit()

        result = await get_current_user("valid_token", db=db_session)

        assert result.id == 123
        assert result.username == "testuser"

    @pytest.mark.asyncio
    @patch("app.services.auth.decode_access_token")
    async def test_get_current_user_user_not_found(
        self, mock_decode_access_token, db_session
    ):
        """Test case where user is not found in the database."""
        # Configure the mock to return a payload with a non-existent user ID
        mock_decode_access_token.return_value = {
            "sub": 9999
        }  # Use a very large ID that won't exist

        # Test that HTTPException is raised when user is not found
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user("valid_token", db=db_session)

        # Verify the exception details
        assert excinfo.value.status_code == 404
        assert "User not found" in str(excinfo.value)

    @pytest.mark.asyncio
    @patch("app.services.auth.decode_access_token")
    async def test_get_current_user_invalid_token(self, mock_decode_access_token):
        """Test case where token decoding fails and raises an HTTPException."""
        mock_decode_access_token.side_effect = HTTPException(
            status_code=401, detail="Invalid token"
        )

        with pytest.raises(HTTPException) as excinfo:
            await get_current_user("invalid_token")

        assert excinfo.value.status_code == 401
        assert "Invalid token" in str(excinfo.value)

    @pytest.mark.asyncio
    @patch("app.services.auth.decode_access_token")
    @patch("app.services.auth.get_user_by_id")
    async def test_get_current_user_with_numeric_id(
        self, mock_get_user_by_id, mock_decode_access_token
    ):
        """Test get_current_user with a numeric user ID."""
        # Setup
        mock_decode_access_token.return_value = {"sub": 123}
        mock_user = MagicMock(spec=User)
        mock_get_user_by_id.return_value = mock_user
        mock_db = MagicMock()

        # Execute
        result = await get_current_user("valid_token", mock_db)

        # Assert
        assert result == mock_user
        mock_decode_access_token.assert_called_once_with("valid_token")
        mock_get_user_by_id.assert_called_once_with(mock_db, 123)

    @pytest.mark.asyncio
    @patch("app.services.auth.decode_access_token")
    @patch("app.services.auth.get_user_by_id")
    async def test_get_current_user_with_string_numeric_id(
        self, mock_get_user_by_id, mock_decode_access_token
    ):
        """Test get_current_user with a string numeric user ID."""
        # Setup
        mock_decode_access_token.return_value = {"sub": "123"}
        mock_user = MagicMock(spec=User)
        mock_get_user_by_id.return_value = mock_user
        mock_db = MagicMock()

        # Execute
        result = await get_current_user("valid_token", mock_db)

        # Assert
        assert result == mock_user
        mock_decode_access_token.assert_called_once_with("valid_token")
        mock_get_user_by_id.assert_called_once_with(mock_db, 123)

    @pytest.mark.asyncio
    @patch("app.services.auth.decode_access_token")
    @patch("app.services.auth.get_user_by_id")
    async def test_get_current_user_with_prefixed_id(
        self, mock_get_user_by_id, mock_decode_access_token
    ):
        """Test get_current_user with a prefixed user ID."""
        # Setup
        mock_decode_access_token.return_value = {"sub": "user_id_123"}
        mock_user = MagicMock(spec=User)
        mock_get_user_by_id.return_value = mock_user
        mock_db = MagicMock()

        # Execute
        result = await get_current_user("valid_token", mock_db)

        # Assert
        assert result == mock_user
        mock_decode_access_token.assert_called_once_with("valid_token")
        mock_get_user_by_id.assert_called_once_with(mock_db, 123)

    @pytest.mark.asyncio
    @patch("app.services.auth.decode_access_token")
    async def test_get_current_user_missing_sub(self, mock_decode_access_token):
        """Test get_current_user with a token missing the 'sub' claim."""
        # Setup
        mock_decode_access_token.return_value = {}  # No 'sub' claim
        mock_db = MagicMock()

        # Execute & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user("valid_token", mock_db)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in str(excinfo.value.detail)
        assert excinfo.value.headers["WWW-Authenticate"] == "Bearer"

    @pytest.mark.asyncio
    @patch("app.services.auth.decode_access_token")
    @patch("app.services.auth.get_user_by_id")
    async def test_get_current_user_invalid_id_format(
        self, mock_get_user_by_id, mock_decode_access_token
    ):
        """Test get_current_user with an invalid ID format."""
        # Setup
        mock_decode_access_token.return_value = {"sub": "invalid_format"}
        mock_get_user_by_id.return_value = None
        mock_db = MagicMock()

        # Execute & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user("valid_token", mock_db)
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in str(excinfo.value.detail)

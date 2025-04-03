"""
Debug script to identify type conversion issues in the application.
"""

import asyncio
import logging
import inspect
import traceback
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.user import get_user_by_id
from app.services.auth import get_current_user
from app.services.jwt_utils import create_access_token

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("debug_script")


async def debug_type_conversion_issues():
    """Debug type conversion issues with user IDs."""
    logger.info("=== Debugging Type Conversion Issues ===")

    # Examine the get_user_by_id function
    logger.info(f"get_user_by_id signature: {inspect.signature(get_user_by_id)}")
    logger.info(f"get_user_by_id source:\n{inspect.getsource(get_user_by_id)}")

    # Test with direct function call using different ID types
    logger.info("\n=== Testing direct function calls with different ID types ===")

    # Create a properly mocked session
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_session.execute.return_value = mock_result
    mock_result.scalars.return_value.first.return_value = MagicMock(id=123)

    # Test with integer ID
    logger.info("Testing with integer ID (123)")
    try:
        with patch(
            "app.services.user.get_user_by_id",
            new=AsyncMock(return_value=MagicMock(id=123)),
        ):
            user = await get_user_by_id(mock_session, 123)
            logger.info(f"Success with integer ID: {user}")
    except Exception as e:
        logger.error(f"Error with integer ID: {e}")
        logger.error(traceback.format_exc())

    # Test with string ID (numeric)
    logger.info("\nTesting with string ID (numeric: '123')")
    try:
        with patch(
            "app.services.user.get_user_by_id",
            new=AsyncMock(return_value=MagicMock(id=123)),
        ):
            user = await get_user_by_id(mock_session, "123")
            logger.info(f"Success with string ID (numeric): {user}")
    except Exception as e:
        logger.error(f"Error with string ID (numeric): {e}")
        logger.error(traceback.format_exc())

    # Test with non-numeric string ID
    logger.info("\nTesting with non-numeric string ID ('user_id_123')")
    try:
        with patch(
            "app.services.user.get_user_by_id",
            new=AsyncMock(return_value=MagicMock(id="user_id_123")),
        ):
            user = await get_user_by_id(mock_session, "user_id_123")
            logger.info(f"Success with non-numeric string ID: {user}")
    except Exception as e:
        logger.error(f"Error with non-numeric string ID: {e}")
        logger.error(traceback.format_exc())

    # Test with JWT token containing string user ID
    logger.info("\n=== Testing JWT token with string user ID ===")
    try:
        # Create a token with string user ID
        token_payload = {"sub": "user_id_123"}
        token = create_access_token(token_payload)
        logger.info(f"Created token with payload: {token_payload}")

        # Try to get current user with this token
        try:
            # Mock the token verification and get_user_by_id
            with patch(
                "app.services.auth.decode_access_token", return_value=token_payload
            ):
                with patch(
                    "app.services.auth.get_user_by_id",
                    new=AsyncMock(return_value=MagicMock(id="user_id_123")),
                ):
                    current_user = await get_current_user(token, db=mock_session)
                    logger.info(f"Success with get_current_user: {current_user}")
        except Exception as e:
            logger.error(f"Error in get_current_user with string ID token: {e}")
            logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Error in JWT token test: {e}")
        logger.error(traceback.format_exc())


async def main():
    """Run the debug function."""
    await debug_type_conversion_issues()


if __name__ == "__main__":
    asyncio.run(main())

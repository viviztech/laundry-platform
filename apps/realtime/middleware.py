"""
WebSocket authentication middleware.
Provides JWT authentication for WebSocket connections.
"""
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from apps.accounts.models import User
from urllib.parse import parse_qs
import logging

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token_key):
    """
    Get user from JWT token.

    Args:
        token_key: JWT token string

    Returns:
        User object or AnonymousUser if token is invalid
    """
    try:
        # Decode and validate the token
        token = AccessToken(token_key)
        user_id = token.payload.get('user_id')

        if not user_id:
            logger.warning("Token does not contain user_id")
            return AnonymousUser()

        # Get the user from database
        user = User.objects.get(id=user_id)

        if not user.is_active:
            logger.warning(f"User {user_id} is not active")
            return AnonymousUser()

        return user

    except (TokenError, InvalidToken) as e:
        logger.warning(f"Invalid token: {str(e)}")
        return AnonymousUser()
    except User.DoesNotExist:
        logger.warning(f"User {user_id} does not exist")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"Error getting user from token: {str(e)}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT tokens.

    Supports token from:
    1. Query string: ws://localhost:8000/ws/notifications/?token=xxx
    2. Authorization header: Authorization: Bearer xxx
    """

    async def __call__(self, scope, receive, send):
        """
        Extract token and authenticate user.

        Args:
            scope: Connection scope
            receive: Receive channel
            send: Send channel
        """
        # Try to get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        # If not in query string, try headers
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()

            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix

        # Authenticate user with token
        if token:
            scope['user'] = await get_user_from_token(token)
            logger.info(f"WebSocket connection authenticated for user: {scope['user']}")
        else:
            scope['user'] = AnonymousUser()
            logger.info("WebSocket connection without authentication")

        return await super().__call__(scope, receive, send)

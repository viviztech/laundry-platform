"""
API views for real-time features.
Provides WebSocket connection tokens and connection info.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
import logging

logger = logging.getLogger(__name__)


@extend_schema(
    summary="Get WebSocket connection token",
    description="Generate a JWT token for WebSocket authentication. Use this token to connect to WebSocket endpoints.",
    responses={
        200: OpenApiResponse(
            description="WebSocket connection information with token",
            response={
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'JWT token for WebSocket auth'},
                    'ws_base_url': {'type': 'string', 'description': 'Base WebSocket URL'},
                    'endpoints': {
                        'type': 'object',
                        'description': 'Available WebSocket endpoints',
                        'properties': {
                            'notifications': {'type': 'string'},
                            'order_tracking': {'type': 'string'},
                            'partner': {'type': 'string'},
                        }
                    },
                    'expires_in': {'type': 'integer', 'description': 'Token expiry in seconds'}
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_websocket_token(request):
    """
    Get a JWT token for WebSocket authentication.

    Returns connection information including:
    - JWT token for authentication
    - WebSocket base URL
    - Available WebSocket endpoints
    - Token expiry time

    The token should be passed as a query parameter:
    ws://localhost:8000/ws/notifications/?token=YOUR_TOKEN
    """
    try:
        # Generate JWT token for the user
        token = AccessToken.for_user(request.user)

        # Get WebSocket base URL from settings or use default
        ws_protocol = 'wss' if settings.DEBUG == False else 'ws'
        ws_host = request.get_host()
        ws_base_url = f'{ws_protocol}://{ws_host}/ws'

        # Build response with connection info
        response_data = {
            'token': str(token),
            'ws_base_url': ws_base_url,
            'endpoints': {
                'notifications': f'{ws_base_url}/notifications/?token={str(token)}',
                'order_tracking': f'{ws_base_url}/orders/{{order_id}}/?token={str(token)}',
                'partner': f'{ws_base_url}/partner/?token={str(token)}' if hasattr(request.user, 'partner') else None,
            },
            'expires_in': int(token.lifetime.total_seconds()),
            'user_id': str(request.user.id),
            'is_partner': hasattr(request.user, 'partner'),
        }

        logger.info(f"WebSocket token generated for user {request.user.id}")

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error generating WebSocket token: {str(e)}")
        return Response(
            {'error': 'Failed to generate WebSocket token'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Get WebSocket connection status",
    description="Get information about available WebSocket endpoints and current connection capabilities.",
    responses={
        200: OpenApiResponse(
            description="WebSocket capabilities and endpoint information"
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def websocket_info(request):
    """
    Get information about available WebSocket endpoints.

    Returns details about:
    - Available endpoints for the user
    - WebSocket features enabled
    - User's WebSocket capabilities
    """
    ws_protocol = 'wss' if not settings.DEBUG else 'ws'
    ws_host = request.get_host()

    info = {
        'websocket_enabled': True,
        'protocol': ws_protocol,
        'host': ws_host,
        'available_endpoints': {
            'notifications': {
                'path': '/ws/notifications/',
                'description': 'Real-time notification updates',
                'authentication_required': True,
            },
            'order_tracking': {
                'path': '/ws/orders/<order_id>/',
                'description': 'Real-time order status updates',
                'authentication_required': True,
            },
        },
        'features': {
            'live_notifications': True,
            'order_tracking': True,
            'mark_read': True,
            'auto_reconnect': True,
        },
        'user_capabilities': {
            'is_authenticated': request.user.is_authenticated,
            'is_partner': hasattr(request.user, 'partner'),
            'is_admin': request.user.is_staff or request.user.is_superuser,
        }
    }

    # Add partner endpoint if user is a partner
    if hasattr(request.user, 'partner'):
        info['available_endpoints']['partner'] = {
            'path': '/ws/partner/',
            'description': 'Partner-specific real-time updates',
            'authentication_required': True,
        }
        info['features']['partner_updates'] = True

    return Response(info, status=status.HTTP_200_OK)

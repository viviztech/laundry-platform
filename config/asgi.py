"""
ASGI config for LaundryConnect project.

It exposes the ASGI callable as a module-level variable named ``application``.

Supports both HTTP and WebSocket connections using Django Channels.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from apps.realtime.middleware import JWTAuthMiddleware
from apps.realtime import routing as realtime_routing
from apps.chat import routing as chat_routing
from apps.tracking import routing as tracking_routing

application = ProtocolTypeRouter({
    # HTTP requests are handled by Django's ASGI application
    "http": django_asgi_app,

    # WebSocket connections are handled by Channels with JWT authentication
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                realtime_routing.websocket_urlpatterns +
                chat_routing.websocket_urlpatterns +
                tracking_routing.websocket_urlpatterns
            )
        )
    ),
})

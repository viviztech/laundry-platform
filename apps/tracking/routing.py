"""
WebSocket routing for Tracking app.
"""

from django.urls import re_path
from .consumers import LocationTrackingConsumer

websocket_urlpatterns = [
    re_path(r'ws/tracking/(?P<order_id>[^/]+)/$', LocationTrackingConsumer.as_asgi()),
]

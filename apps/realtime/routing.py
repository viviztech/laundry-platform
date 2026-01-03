"""
WebSocket URL routing for LaundryConnect.
Maps WebSocket URLs to consumers.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # Real-time notifications for authenticated users
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),

    # Real-time order tracking
    path('ws/orders/<uuid:order_id>/', consumers.OrderTrackingConsumer.as_asgi()),

    # Partner real-time updates
    path('ws/partner/', consumers.PartnerConsumer.as_asgi()),
]

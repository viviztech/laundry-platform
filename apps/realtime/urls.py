"""
URL patterns for real-time app HTTP endpoints.
"""
from django.urls import path
from . import views

app_name = 'realtime'

urlpatterns = [
    # WebSocket connection token
    path('token/', views.get_websocket_token, name='websocket-token'),

    # WebSocket information
    path('info/', views.websocket_info, name='websocket-info'),
]

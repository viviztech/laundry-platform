"""
URL configuration for Chat app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ChatRoomViewSet, ChatMessageViewSet, TypingIndicatorViewSet

app_name = 'chat'

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')
router.register(r'messages', ChatMessageViewSet, basename='chatmessage')

urlpatterns = [
    path('', include(router.urls)),
    path('typing/start/', TypingIndicatorViewSet.as_view({'post': 'start'}), name='typing-start'),
    path('typing/stop/', TypingIndicatorViewSet.as_view({'post': 'stop'}), name='typing-stop'),
]

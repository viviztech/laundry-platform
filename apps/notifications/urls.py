"""
URL configuration for notifications app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet,
    NotificationTemplateViewSet,
    NotificationPreferenceViewSet,
    BulkNotificationViewSet,
    PushSubscriptionViewSet,
)

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'templates', NotificationTemplateViewSet, basename='template')
router.register(r'preferences', NotificationPreferenceViewSet, basename='preference')
router.register(r'bulk', BulkNotificationViewSet, basename='bulk')
router.register(r'push-subscriptions', PushSubscriptionViewSet, basename='push-subscription')

urlpatterns = [
    path('', include(router.urls)),
]

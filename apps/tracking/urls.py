"""
URL configuration for Tracking app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LocationUpdateViewSet, RouteViewSet, TrackingSessionViewSet

app_name = 'tracking'

router = DefaultRouter()
router.register(r'locations', LocationUpdateViewSet, basename='location')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'sessions', TrackingSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]

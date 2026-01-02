"""
URL configuration for partners app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PartnerViewSet,
    PartnerServiceAreaViewSet,
    PartnerAvailabilityViewSet,
    PartnerHolidayViewSet,
)

app_name = 'partners'

router = DefaultRouter()
router.register(r'partners', PartnerViewSet, basename='partner')
router.register(r'service-areas', PartnerServiceAreaViewSet, basename='service-area')
router.register(r'availability', PartnerAvailabilityViewSet, basename='availability')
router.register(r'holidays', PartnerHolidayViewSet, basename='holiday')

urlpatterns = [
    path('', include(router.urls)),
]

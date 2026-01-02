"""
URL configuration for services app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ServiceCategoryViewSet,
    GarmentTypeViewSet,
    ServiceViewSet,
    PricingZoneViewSet,
    AddonViewSet,
    ServiceCatalogView,
)

app_name = 'services'

router = DefaultRouter()
router.register(r'categories', ServiceCategoryViewSet, basename='category')
router.register(r'garments', GarmentTypeViewSet, basename='garment')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'zones', PricingZoneViewSet, basename='zone')
router.register(r'addons', AddonViewSet, basename='addon')

urlpatterns = [
    path('catalog/', ServiceCatalogView.as_view(), name='catalog'),
    path('', include(router.urls)),
]

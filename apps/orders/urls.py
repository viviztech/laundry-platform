"""
URL configuration for orders app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet
from .partner_views import PartnerOrderViewSet

app_name = 'orders'

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'partner/orders', PartnerOrderViewSet, basename='partner-order')

urlpatterns = [
    path('', include(router.urls)),
]

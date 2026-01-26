"""URL configuration for AI app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecommendationViewSet,
    PriceEstimationViewSet,
    DemandForecastViewSet,
    FraudDetectionViewSet,
    GarmentRecognitionViewSet,
    MLModelViewSet
)

app_name = 'ai'

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'prices', PriceEstimationViewSet, basename='price')
router.register(r'forecasts', DemandForecastViewSet, basename='forecast')
router.register(r'fraud', FraudDetectionViewSet, basename='fraud')
router.register(r'garments', GarmentRecognitionViewSet, basename='garment')
router.register(r'models', MLModelViewSet, basename='model')

urlpatterns = [
    path('', include(router.urls)),
]

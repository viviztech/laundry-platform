"""DRF serializers for AI models."""

from rest_framework import serializers
from .models import (
    GarmentRecognition,
    PriceEstimation,
    DemandForecast,
    Recommendation,
    FraudDetection,
    MLModel
)


class GarmentRecognitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GarmentRecognition
        fields = [
            'id', 'image', 'garment_type', 'garment_category',
            'fabric_type', 'color_primary', 'has_stains', 'has_damages',
            'confidence_level', 'confidence_score', 'estimated_price',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PriceEstimationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceEstimation
        fields = [
            'id', 'garment_type', 'service_type', 'urgency_level',
            'base_price', 'recommended_price', 'min_price', 'max_price',
            'profit_margin', 'conversion_probability', 'confidence_score',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DemandForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandForecast
        fields = [
            'id', 'forecast_date', 'predicted_order_count',
            'predicted_revenue', 'prediction_lower_bound',
            'prediction_upper_bound', 'confidence_score',
            'is_weekend', 'trend_direction', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecommendationSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    addon_name = serializers.CharField(source='addon.name', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'recommendation_type', 'service', 'service_name',
            'addon', 'addon_name', 'title', 'description',
            'relevance_score', 'confidence_score', 'reason_description',
            'estimated_savings', 'was_shown', 'was_clicked', 'was_accepted',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FraudDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudDetection
        fields = [
            'id', 'risk_score', 'risk_level', 'fraud_indicators',
            'velocity_score', 'pattern_score', 'device_score',
            'location_score', 'recommended_action', 'status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = [
            'id', 'name', 'model_type', 'version', 'description',
            'framework', 'algorithm', 'accuracy', 'status',
            'deployed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

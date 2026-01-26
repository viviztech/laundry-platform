"""Django admin for AI models."""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    GarmentRecognition,
    PriceEstimation,
    DemandForecast,
    Recommendation,
    FraudDetection,
    MLModel
)


@admin.register(GarmentRecognition)
class GarmentRecognitionAdmin(admin.ModelAdmin):
    list_display = ['garment_type', 'user', 'confidence_badge', 'estimated_price', 'created_at']
    list_filter = ['confidence_level', 'garment_type', 'has_stains', 'has_damages']
    search_fields = ['user__email', 'garment_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def confidence_badge(self, obj):
        colors = {'high': '#28a745', 'medium': '#ffc107', 'low': '#dc3545'}
        color = colors.get(obj.confidence_level, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_confidence_level_display()
        )
    confidence_badge.short_description = 'Confidence'


@admin.register(PriceEstimation)
class PriceEstimationAdmin(admin.ModelAdmin):
    list_display = ['garment_type', 'service_type', 'recommended_price', 'confidence_score', 'created_at']
    list_filter = ['service_type', 'urgency_level']
    search_fields = ['garment_type']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ['forecast_date', 'predicted_order_count', 'predicted_revenue', 'confidence_score', 'trend_badge']
    list_filter = ['granularity', 'trend_direction', 'is_weekend']
    search_fields = ['forecast_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def trend_badge(self, obj):
        colors = {'increasing': '#28a745', 'stable': '#6c757d', 'decreasing': '#dc3545'}
        color = colors.get(obj.trend_direction, '#6c757d')
        return format_html(
            '<span style="color: {};">● {}</span>',
            color, obj.get_trend_direction_display()
        )
    trend_badge.short_description = 'Trend'


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type_badge', 'title', 'relevance_score', 'status_badges', 'created_at']
    list_filter = ['recommendation_type', 'was_shown', 'was_accepted']
    search_fields = ['user__email', 'title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def type_badge(self, obj):
        return format_html(
            '<span style="background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_recommendation_type_display()
        )
    type_badge.short_description = 'Type'
    
    def status_badges(self, obj):
        badges = []
        if obj.was_shown:
            badges.append('<span style="background: #28a745; color: white; padding: 2px 4px; border-radius: 2px; font-size: 10px;">SHOWN</span>')
        if obj.was_clicked:
            badges.append('<span style="background: #17a2b8; color: white; padding: 2px 4px; border-radius: 2px; font-size: 10px;">CLICKED</span>')
        if obj.was_accepted:
            badges.append('<span style="background: #ffc107; color: black; padding: 2px 4px; border-radius: 2px; font-size: 10px;">ACCEPTED</span>')
        return format_html('{}', ' '.join(badges) if badges else '-')
    status_badges.short_description = 'Status'


@admin.register(FraudDetection)
class FraudDetectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'order', 'risk_badge', 'risk_score', 'status_badge', 'recommended_action', 'created_at']
    list_filter = ['risk_level', 'status', 'recommended_action']
    search_fields = ['user__email', 'order__order_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    actions = ['approve_cases', 'review_cases']
    
    def risk_badge(self, obj):
        colors = {'low': '#28a745', 'medium': '#ffc107', 'high': '#fd7e14', 'critical': '#dc3545'}
        color = colors.get(obj.risk_level, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_risk_level_display().upper()
        )
    risk_badge.short_description = 'Risk Level'
    
    def status_badge(self, obj):
        colors = {'pending': '#6c757d', 'reviewing': '#007bff', 'approved': '#28a745', 'blocked': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_cases(self, request, queryset):
        queryset.update(status='approved', reviewed_by=request.user)
        self.message_user(request, f'{queryset.count()} cases approved')
    approve_cases.short_description = 'Approve selected cases'
    
    def review_cases(self, request, queryset):
        queryset.update(status='reviewing')
        self.message_user(request, f'{queryset.count()} cases marked for review')
    review_cases.short_description = 'Mark for review'


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_badge', 'version', 'status_badge', 'accuracy', 'deployed_at']
    list_filter = ['model_type', 'status', 'framework']
    search_fields = ['name', 'version']
    readonly_fields = ['id', 'created_at', 'updated_at', 'prediction_count']
    
    def type_badge(self, obj):
        return format_html(
            '<span style="background: #6610f2; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_model_type_display()
        )
    type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        colors = {'training': '#6c757d', 'testing': '#17a2b8', 'staging': '#ffc107', 'production': '#28a745', 'deprecated': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

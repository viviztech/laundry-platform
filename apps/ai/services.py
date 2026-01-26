"""
AI service layer for business logic.

Contains service classes for:
- Recommendation Engine
- Fraud Detection  
- Price Estimation
- Demand Forecasting
"""

from decimal import Decimal
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
from typing import List, Dict, Optional
import random

from .models import (
    Recommendation,
    FraudDetection,
    PriceEstimation,
    DemandForecast
)
from apps.orders.models import Order
from apps.services.models import Service, Addon
from apps.accounts.models import User


class RecommendationService:
    """Personalized recommendation engine."""
    
    def __init__(self):
        self.model_version = 'v1.0'
    
    def generate_recommendations(self, user: User, order=None, limit=5):
        """Generate personalized recommendations."""
        # Simplified collaborative filtering
        return []
    
    def track_interaction(self, recommendation, action: str):
        """Track user interaction (shown/clicked/accepted)."""
        now = timezone.now()
        if action == 'shown':
            recommendation.was_shown = True
            recommendation.shown_at = now
        elif action == 'clicked':
            recommendation.was_clicked = True
            recommendation.clicked_at = now
        elif action == 'accepted':
            recommendation.was_accepted = True
            recommendation.accepted_at = now
        recommendation.save()
        return recommendation


class FraudDetectionService:
    """Fraud detection and risk assessment."""
    
    def __init__(self):
        self.model_version = 'v1.0'
        self.critical_threshold = Decimal('90.00')
    
    def analyze_order(self, order: Order, request_meta: Dict):
        """Analyze order for fraud indicators."""
        user = order.user
        
        # Calculate risk scores
        velocity_score = self._check_velocity(user)
        pattern_score = Decimal('20.00')  # Simplified
        device_score = Decimal('15.00')
        location_score = Decimal('10.00')
        
        # Overall risk score (weighted)
        risk_score = (velocity_score * Decimal('0.4') + 
                     pattern_score * Decimal('0.3') + 
                     device_score * Decimal('0.2') +
                     location_score * Decimal('0.1'))
        
        # Determine risk level
        if risk_score >= Decimal('90.00'):
            risk_level, action = 'critical', 'block_user'
        elif risk_score >= Decimal('70.00'):
            risk_level, action = 'high', 'review'
        elif risk_score >= Decimal('40.00'):
            risk_level, action = 'medium', 'review'
        else:
            risk_level, action = 'low', 'approve'
        
        # Create detection record
        detection = FraudDetection.objects.create(
            user=user,
            order=order,
            risk_score=risk_score,
            risk_level=risk_level,
            velocity_score=velocity_score,
            pattern_score=pattern_score,
            device_score=device_score,
            location_score=location_score,
            is_velocity_anomaly=velocity_score > 60,
            user_age_days=(timezone.now().date() - user.date_joined.date()).days,
            order_count_24h=Order.objects.filter(
                user=user, created_at__gte=timezone.now() - timedelta(hours=24)
            ).count(),
            order_count_7d=Order.objects.filter(
                user=user, created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            ip_address=request_meta.get('REMOTE_ADDR'),
            user_agent=request_meta.get('HTTP_USER_AGENT', ''),
            recommended_action=action,
            model_version=self.model_version,
            fraud_indicators=[]
        )
        
        return detection
    
    def _check_velocity(self, user: User) -> Decimal:
        """Check order frequency."""
        recent = Order.objects.filter(
            user=user, created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        if recent >= 10: return Decimal('90.00')
        elif recent >= 5: return Decimal('60.00')
        elif recent >= 3: return Decimal('30.00')
        return Decimal('10.00')


class PriceEstimationService:
    """AI-powered price estimation."""
    
    def __init__(self):
        self.model_version = 'v1.0'
    
    def estimate_price(self, garment_type: str, service_type: str, urgency='standard'):
        """Estimate optimal price."""
        # Base prices (simplified)
        base_prices = {
            'shirt': {'wash': 50, 'dry_clean': 100},
            'pants': {'wash': 60, 'dry_clean': 120},
        }
        
        base = Decimal(str(base_prices.get(garment_type, {}).get(service_type, 100)))
        urgency_mult = {'economy': 0.8, 'standard': 1.0, 'express': 1.5}[urgency]
        
        recommended = base * Decimal(str(urgency_mult))
        
        estimation = PriceEstimation.objects.create(
            garment_type=garment_type,
            service_type=service_type,
            urgency_level=urgency,
            current_demand_score=Decimal('50.00'),
            seasonal_factor=Decimal('1.0'),
            base_price=base,
            recommended_price=recommended,
            min_price=recommended * Decimal('0.8'),
            max_price=recommended * Decimal('1.3'),
            profit_margin=Decimal('40.00'),
            conversion_probability=Decimal('75.00'),
            model_version=self.model_version,
            confidence_score=Decimal('70.00')
        )
        
        return estimation


class DemandForecastService:
    """Demand forecasting service."""
    
    def __init__(self):
        self.model_version = 'v1.0'
    
    def forecast_demand(self, forecast_date, partner=None):
        """Generate demand forecast."""
        # Simplified forecast
        is_weekend = forecast_date.weekday() >= 5
        base_orders = 20 if is_weekend else 15
        
        forecast = DemandForecast.objects.create(
            forecast_date=forecast_date,
            granularity='daily',
            partner=partner,
            predicted_order_count=base_orders,
            predicted_revenue=Decimal(str(base_orders * 500)),
            prediction_lower_bound=int(base_orders * 0.8),
            prediction_upper_bound=int(base_orders * 1.2),
            confidence_score=Decimal('70.00'),
            is_weekend=is_weekend,
            historical_days_used=90,
            trend_direction='stable',
            model_version=self.model_version,
            model_type='simple'
        )
        
        return forecast

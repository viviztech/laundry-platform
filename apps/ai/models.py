"""
AI & Machine Learning models for LaundryConnect platform.

This module contains models for:
- Garment recognition and image analysis
- Price estimation and optimization
- Demand forecasting
- Recommendations
- Fraud detection
"""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class GarmentRecognition(models.Model):
    """
    Store garment recognition results from image analysis.

    Uses computer vision to identify garment types, colors, fabric,
    stains, and damages from uploaded images.
    """

    CONFIDENCE_CHOICES = [
        ('high', 'High (>80%)'),
        ('medium', 'Medium (50-80%)'),
        ('low', 'Low (<50%)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Related entities
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='garment_recognitions',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='garment_recognitions'
    )

    # Image data
    image = models.ImageField(upload_to='garment_images/%Y/%m/%d/')
    image_url = models.URLField(max_length=500, blank=True)

    # Recognition results
    garment_type = models.CharField(max_length=100)  # shirt, pants, dress, etc.
    garment_category = models.CharField(max_length=50)  # casual, formal, sports, etc.
    fabric_type = models.CharField(max_length=100, blank=True)  # cotton, silk, wool, etc.
    color_primary = models.CharField(max_length=50, blank=True)
    color_secondary = models.CharField(max_length=50, blank=True)

    # Condition analysis
    has_stains = models.BooleanField(default=False)
    stain_locations = models.JSONField(default=list, blank=True)  # [{"type": "oil", "location": "front", "severity": "medium"}]
    has_damages = models.BooleanField(default=False)
    damage_details = models.JSONField(default=list, blank=True)  # [{"type": "tear", "location": "sleeve", "size": "small"}]

    # Care instructions detected
    care_instructions = models.JSONField(default=dict, blank=True)  # {"wash": "cold", "dry": "low", "iron": "medium"}
    special_requirements = models.JSONField(default=list, blank=True)  # ["dry clean only", "hand wash"]

    # Confidence scores
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES, default='medium')
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Confidence score from 0 to 100"
    )

    # AI model details
    model_version = models.CharField(max_length=50, default='v1.0')
    processing_time_ms = models.IntegerField(help_text="Processing time in milliseconds")

    # Raw AI response
    raw_response = models.JSONField(default=dict, blank=True)

    # Estimated pricing (auto-calculated)
    estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="AI-estimated service price"
    )

    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_recognitions'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'garment_recognitions'
        verbose_name = 'Garment Recognition'
        verbose_name_plural = 'Garment Recognitions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['order', '-created_at']),
            models.Index(fields=['garment_type', '-created_at']),
            models.Index(fields=['confidence_level']),
        ]

    def __str__(self):
        return f"{self.garment_type} - {self.confidence_level} confidence"


class PriceEstimation(models.Model):
    """
    AI-powered price estimation for services.

    Uses machine learning to predict optimal pricing based on
    garment type, market conditions, demand, and historical data.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Related entities
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='price_estimations',
        null=True,
        blank=True
    )
    garment_recognition = models.ForeignKey(
        GarmentRecognition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='price_estimations'
    )

    # Input features
    garment_type = models.CharField(max_length=100)
    fabric_type = models.CharField(max_length=100, blank=True)
    service_type = models.CharField(max_length=50)  # wash, dry_clean, iron, etc.
    urgency_level = models.CharField(max_length=20, default='standard')  # express, standard, economy

    # Market factors
    current_demand_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('50.00'),
        help_text="Demand score 0-100"
    )
    competitor_avg_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    seasonal_factor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text="Seasonal multiplier (0.5 - 2.0)"
    )

    # Location factors
    location_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    pricing_zone = models.CharField(max_length=50, blank=True)

    # AI predictions
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    recommended_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Optimization factors
    profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Estimated profit margin percentage"
    )
    conversion_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Probability of customer accepting this price (0-100)"
    )

    # Model details
    model_version = models.CharField(max_length=50, default='v1.0')
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Features used
    features_used = models.JSONField(default=dict, blank=True)

    # Actual outcome (for model training)
    actual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual price charged"
    )
    was_accepted = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether customer accepted the price"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'price_estimations'
        verbose_name = 'Price Estimation'
        verbose_name_plural = 'Price Estimations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service', '-created_at']),
            models.Index(fields=['garment_type', 'service_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.garment_type} {self.service_type} - ₹{self.recommended_price}"


class DemandForecast(models.Model):
    """
    Demand forecasting for order volume prediction.

    Predicts order volumes for capacity planning and resource allocation.
    """

    GRANULARITY_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Forecast period
    forecast_date = models.DateField(db_index=True)
    forecast_hour = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(23)]
    )
    granularity = models.CharField(max_length=20, choices=GRANULARITY_CHOICES, default='daily')

    # Geographic scope
    partner = models.ForeignKey(
        'partners.Partner',
        on_delete=models.CASCADE,
        related_name='demand_forecasts',
        null=True,
        blank=True
    )
    service_area = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Predictions
    predicted_order_count = models.IntegerField()
    predicted_revenue = models.DecimalField(max_digits=12, decimal_places=2)

    # Confidence intervals
    prediction_lower_bound = models.IntegerField(help_text="Lower bound of 95% confidence interval")
    prediction_upper_bound = models.IntegerField(help_text="Upper bound of 95% confidence interval")
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Category breakdown
    category_breakdown = models.JSONField(
        default=dict,
        blank=True,
        help_text="Predicted orders by service category"
    )

    # External factors
    is_holiday = models.BooleanField(default=False)
    is_weekend = models.BooleanField(default=False)
    weather_condition = models.CharField(max_length=50, blank=True)
    special_event = models.CharField(max_length=200, blank=True)

    # Historical data used
    historical_days_used = models.IntegerField(default=90)
    trend_direction = models.CharField(
        max_length=20,
        choices=[('increasing', 'Increasing'), ('stable', 'Stable'), ('decreasing', 'Decreasing')],
        default='stable'
    )

    # Model details
    model_version = models.CharField(max_length=50, default='v1.0')
    model_type = models.CharField(
        max_length=50,
        default='lstm',
        help_text="Model type: lstm, arima, prophet, etc."
    )

    # Actual outcome (for model evaluation)
    actual_order_count = models.IntegerField(null=True, blank=True)
    actual_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    prediction_error = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Absolute percentage error"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'demand_forecasts'
        verbose_name = 'Demand Forecast'
        verbose_name_plural = 'Demand Forecasts'
        ordering = ['-forecast_date', '-created_at']
        indexes = [
            models.Index(fields=['forecast_date', 'granularity']),
            models.Index(fields=['partner', 'forecast_date']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['forecast_date', 'forecast_hour', 'partner', 'granularity']]

    def __str__(self):
        if self.forecast_hour is not None:
            return f"Forecast {self.forecast_date} {self.forecast_hour}:00 - {self.predicted_order_count} orders"
        return f"Forecast {self.forecast_date} - {self.predicted_order_count} orders"


class Recommendation(models.Model):
    """
    Personalized service recommendations for users.

    Uses collaborative filtering and content-based filtering to suggest
    services, add-ons, and offers to customers.
    """

    RECOMMENDATION_TYPE_CHOICES = [
        ('service', 'Service Recommendation'),
        ('addon', 'Add-on Suggestion'),
        ('upsell', 'Upsell Opportunity'),
        ('cross_sell', 'Cross-sell Item'),
        ('offer', 'Personalized Offer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User and context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_recommendations'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='ai_recommendations',
        null=True,
        blank=True
    )

    # Recommendation details
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)

    # Recommended item
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='ai_recommendations',
        null=True,
        blank=True
    )
    addon = models.ForeignKey(
        'services.Addon',
        on_delete=models.CASCADE,
        related_name='ai_recommendations',
        null=True,
        blank=True
    )

    # Recommendation strength
    relevance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How relevant this recommendation is (0-100)"
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Reasoning
    reason_code = models.CharField(max_length=50)  # frequently_bought_together, similar_users, etc.
    reason_description = models.TextField(blank=True)

    # Features that influenced recommendation
    influencing_factors = models.JSONField(
        default=list,
        blank=True,
        help_text="Factors that led to this recommendation"
    )

    # Similar users/items used
    similar_user_ids = models.JSONField(default=list, blank=True)
    similar_order_ids = models.JSONField(default=list, blank=True)

    # Display info
    title = models.CharField(max_length=200)
    description = models.TextField()
    estimated_savings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # User interaction
    was_shown = models.BooleanField(default=False)
    shown_at = models.DateTimeField(null=True, blank=True)
    was_clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    was_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    # Model details
    model_version = models.CharField(max_length=50, default='v1.0')
    algorithm_used = models.CharField(
        max_length=50,
        default='collaborative_filtering',
        help_text="Algorithm: collaborative_filtering, content_based, hybrid"
    )

    # Expiry
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this recommendation expires"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_recommendations'
        verbose_name = 'AI Recommendation'
        verbose_name_plural = 'AI Recommendations'
        ordering = ['-relevance_score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['order', '-relevance_score']),
            models.Index(fields=['recommendation_type', '-relevance_score']),
            models.Index(fields=['was_shown', 'was_accepted']),
        ]

    def __str__(self):
        return f"{self.recommendation_type} for {self.user.email} - {self.relevance_score}%"


class FraudDetection(models.Model):
    """
    Fraud detection and risk scoring for orders and payments.

    Uses anomaly detection and pattern recognition to identify
    suspicious activities and prevent fraud.
    """

    RISK_LEVEL_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('approved', 'Approved - Not Fraud'),
        ('blocked', 'Blocked - Fraud Detected'),
        ('false_positive', 'False Positive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Related entities
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fraud_detections'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='fraud_detections',
        null=True,
        blank=True
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.CASCADE,
        related_name='fraud_detections',
        null=True,
        blank=True
    )

    # Risk assessment
    risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall risk score (0-100)"
    )
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, db_index=True)

    # Fraud indicators
    fraud_indicators = models.JSONField(
        default=list,
        help_text="List of detected fraud indicators"
    )

    # Anomaly scores
    velocity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Transaction velocity anomaly score"
    )
    pattern_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Behavioral pattern anomaly score"
    )
    device_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Device fingerprint anomaly score"
    )
    location_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Location anomaly score"
    )

    # Suspicious patterns detected
    is_velocity_anomaly = models.BooleanField(default=False)  # Too many orders in short time
    is_pattern_anomaly = models.BooleanField(default=False)  # Unusual behavior
    is_device_mismatch = models.BooleanField(default=False)  # New/suspicious device
    is_location_anomaly = models.BooleanField(default=False)  # Unusual location
    is_payment_anomaly = models.BooleanField(default=False)  # Suspicious payment pattern

    # Context data
    user_age_days = models.IntegerField(help_text="Account age in days")
    order_count_24h = models.IntegerField(default=0)
    order_count_7d = models.IntegerField(default=0)
    failed_payment_count = models.IntegerField(default=0)

    # Device/location info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_fingerprint = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)

    # Recommendation
    recommended_action = models.CharField(
        max_length=50,
        choices=[
            ('approve', 'Approve'),
            ('review', 'Manual Review'),
            ('decline', 'Decline'),
            ('block_user', 'Block User'),
        ],
        default='review'
    )

    # Status and resolution
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_fraud_cases'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    # Model details
    model_version = models.CharField(max_length=50, default='v1.0')
    detection_rules = models.JSONField(default=list, blank=True)

    # Auto-action taken
    auto_action_taken = models.CharField(max_length=50, blank=True)
    action_taken_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fraud_detections'
        verbose_name = 'Fraud Detection'
        verbose_name_plural = 'Fraud Detections'
        ordering = ['-risk_score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['order', '-created_at']),
            models.Index(fields=['risk_level', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-risk_score', '-created_at']),
        ]

    def __str__(self):
        return f"{self.risk_level} - {self.user.email} - Score: {self.risk_score}"


class MLModel(models.Model):
    """
    Metadata for ML models used in the platform.

    Tracks model versions, performance metrics, and deployment status.
    """

    MODEL_TYPE_CHOICES = [
        ('garment_recognition', 'Garment Recognition'),
        ('price_estimation', 'Price Estimation'),
        ('demand_forecast', 'Demand Forecasting'),
        ('recommendation', 'Recommendation Engine'),
        ('fraud_detection', 'Fraud Detection'),
        ('chatbot', 'Chatbot NLP'),
    ]

    STATUS_CHOICES = [
        ('training', 'Training'),
        ('testing', 'Testing'),
        ('staging', 'Staging'),
        ('production', 'Production'),
        ('deprecated', 'Deprecated'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Model identification
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES, db_index=True)
    version = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    # Model details
    framework = models.CharField(max_length=50)  # tensorflow, pytorch, scikit-learn, etc.
    algorithm = models.CharField(max_length=100)
    hyperparameters = models.JSONField(default=dict, blank=True)

    # Training details
    training_dataset_size = models.IntegerField(null=True, blank=True)
    training_start_date = models.DateTimeField(null=True, blank=True)
    training_end_date = models.DateTimeField(null=True, blank=True)
    training_duration_seconds = models.IntegerField(null=True, blank=True)

    # Performance metrics
    accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Model accuracy percentage"
    )
    precision = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recall = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    f1_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Additional metrics
    performance_metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional performance metrics"
    )

    # Deployment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='training', db_index=True)
    deployed_at = models.DateTimeField(null=True, blank=True)
    deployment_url = models.URLField(max_length=500, blank=True)

    # Model file
    model_file_path = models.CharField(max_length=500, blank=True)
    model_file_size_mb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Usage statistics
    prediction_count = models.IntegerField(default=0)
    avg_inference_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Average inference time in milliseconds"
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_models'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ml_models'
        verbose_name = 'ML Model'
        verbose_name_plural = 'ML Models'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_type', 'status']),
            models.Index(fields=['version']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} {self.version} - {self.status}"

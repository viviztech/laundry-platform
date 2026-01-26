"""
Admin Panel Configuration for Partner Launch
Controls which modules are visible in the admin panel
"""

# =============================================================================
# PRIORITY MODULES - Always Visible
# =============================================================================
CORE_MODULES = {
    'accounts': ['User', 'UserProfile', 'Address'],
    'partners': ['Partner', 'PartnerAvailability', 'PartnerServiceArea', 'PartnerHoliday'],
    'orders': ['Order', 'OrderItem', 'OrderStatusHistory'],
    'services': ['ServiceCategory', 'GarmentType', 'Service', 'PricingZone', 'ServicePricing'],
    'payments': ['Payment', 'Wallet', 'WalletTransaction'],
    'chat': ['ChatRoom', 'ChatMessage'],
    'notifications': ['NotificationPreference', 'Notification'],
}

# =============================================================================
# OPTIONAL MODULES - Hidden for Partner Launch (Can be enabled later)
# =============================================================================
OPTIONAL_MODULES = {
    'ai': ['GarmentRecognition', 'PriceEstimation', 'DemandForecast', 'Recommendation', 'FraudDetection', 'MLModel'],
    'analytics': ['DailyRevenueSummary', 'PartnerPerformanceMetric', 'CustomerAnalytics', 'ReportSchedule', 'AnalyticsCache'],
    'tracking': ['LocationUpdate', 'Route', 'TrackingSession'],
    'orders': ['OrderAddon', 'OrderRating'],  # Less critical order features
    'payments': ['Refund', 'PaymentMethod'],  # Advanced payment features
    'chat': ['TypingIndicator'],  # Nice-to-have chat feature
    'notifications': ['NotificationTemplate', 'PushSubscription'],  # Advanced notification features
    'services': ['Addon'],  # Service add-ons
    'partners': ['PartnerPerformance'],  # Detailed performance metrics (use dashboard instead)
}

# =============================================================================
# FEATURE FLAGS
# =============================================================================
# Set to True to enable optional modules
ENABLE_AI_FEATURES = False
ENABLE_ANALYTICS_DETAILED = False
ENABLE_LOCATION_TRACKING = False
ENABLE_ADVANCED_PAYMENTS = False
ENABLE_ADVANCED_NOTIFICATIONS = False
ENABLE_SERVICE_ADDONS = False

def should_register_model(app_label, model_name):
    """
    Determine if a model should be registered in admin panel.

    Args:
        app_label: Django app label (e.g., 'partners')
        model_name: Model class name (e.g., 'Partner')

    Returns:
        bool: True if model should be visible in admin
    """
    # Always show core modules
    if app_label in CORE_MODULES and model_name in CORE_MODULES[app_label]:
        return True

    # Check feature flags for optional modules
    if app_label == 'ai' and ENABLE_AI_FEATURES:
        return True

    if app_label == 'analytics' and ENABLE_ANALYTICS_DETAILED:
        return True

    if app_label == 'tracking' and ENABLE_LOCATION_TRACKING:
        return True

    if app_label == 'payments' and model_name in ['Refund', 'PaymentMethod'] and ENABLE_ADVANCED_PAYMENTS:
        return True

    if app_label == 'notifications' and model_name in ['NotificationTemplate', 'PushSubscription'] and ENABLE_ADVANCED_NOTIFICATIONS:
        return True

    if app_label == 'services' and model_name == 'Addon' and ENABLE_SERVICE_ADDONS:
        return True

    # Hide everything else
    return False

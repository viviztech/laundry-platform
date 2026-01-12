"""
Django admin configuration for Analytics models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django.urls import reverse

from .models import (
    DailyRevenueSummary,
    PartnerPerformanceMetric,
    CustomerAnalytics,
    ReportSchedule,
    AnalyticsCache
)


@admin.register(DailyRevenueSummary)
class DailyRevenueSummaryAdmin(admin.ModelAdmin):
    """Admin interface for Daily Revenue Summary."""

    list_display = [
        'date',
        'revenue_display',
        'order_count',
        'avg_order_value_display',
        'completion_indicator',
        'refund_display',
        'created_at',
    ]
    list_filter = [
        'date',
        'created_at',
    ]
    search_fields = ['date']
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'net_revenue',
        'cancellation_rate',
    ]
    fieldsets = [
        ('Date', {
            'fields': ['id', 'date']
        }),
        ('Revenue Metrics', {
            'fields': [
                'total_revenue',
                'net_revenue',
                'order_count',
                'average_order_value',
            ]
        }),
        ('Revenue by Payment Method', {
            'fields': [
                'cash_revenue',
                'card_revenue',
                'wallet_revenue',
                'online_revenue',
            ]
        }),
        ('Order Status', {
            'fields': [
                'completed_orders',
                'cancelled_orders',
                'pending_orders',
                'cancellation_rate',
            ]
        }),
        ('Customer Metrics', {
            'fields': [
                'new_customers',
                'returning_customers',
            ]
        }),
        ('Refunds', {
            'fields': [
                'refund_amount',
                'refund_count',
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    date_hierarchy = 'date'

    def revenue_display(self, obj):
        """Display revenue with currency."""
        return f"${obj.total_revenue:,.2f}"
    revenue_display.short_description = 'Total Revenue'
    revenue_display.admin_order_field = 'total_revenue'

    def avg_order_value_display(self, obj):
        """Display average order value."""
        return f"${obj.average_order_value:,.2f}"
    avg_order_value_display.short_description = 'Avg Order Value'

    def completion_indicator(self, obj):
        """Show completion rate with color."""
        if obj.order_count == 0:
            return '-'
        rate = (obj.completed_orders / obj.order_count) * 100
        color = '#28a745' if rate >= 80 else '#ffc107' if rate >= 60 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    completion_indicator.short_description = 'Completion Rate'

    def refund_display(self, obj):
        """Display refund amount and count."""
        if obj.refund_count == 0:
            return '-'
        return format_html(
            '${:,.2f} <span style="color: #6c757d;">({} refunds)</span>',
            obj.refund_amount, obj.refund_count
        )
    refund_display.short_description = 'Refunds'


@admin.register(PartnerPerformanceMetric)
class PartnerPerformanceMetricAdmin(admin.ModelAdmin):
    """Admin interface for Partner Performance Metrics."""

    list_display = [
        'partner_link',
        'date',
        'orders_completed',
        'revenue_display',
        'acceptance_rate_display',
        'completion_rate_display',
        'rating_display',
        'issues_indicator',
    ]
    list_filter = [
        'date',
        'partner',
    ]
    search_fields = [
        'partner__business_name',
        'date',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'acceptance_rate',
        'completion_rate',
        'rejection_rate',
    ]
    fieldsets = [
        ('Partner & Date', {
            'fields': ['id', 'partner', 'date']
        }),
        ('Order Metrics', {
            'fields': [
                'orders_received',
                'orders_accepted',
                'orders_rejected',
                'orders_completed',
                'orders_cancelled',
                'acceptance_rate',
                'completion_rate',
                'rejection_rate',
            ]
        }),
        ('Revenue', {
            'fields': ['total_revenue']
        }),
        ('Timing Metrics (minutes)', {
            'fields': [
                'avg_acceptance_time',
                'avg_pickup_time',
                'avg_processing_time',
                'avg_delivery_time',
                'avg_total_time',
            ]
        }),
        ('Quality', {
            'fields': [
                'avg_rating',
                'rating_count',
            ]
        }),
        ('Issues', {
            'fields': [
                'issues_reported',
                'items_damaged',
                'items_lost',
            ]
        }),
        ('Capacity', {
            'fields': ['capacity_utilized_percent']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    date_hierarchy = 'date'

    def partner_link(self, obj):
        """Link to partner."""
        url = reverse('admin:partners_partner_change', args=[obj.partner.id])
        return format_html('<a href="{}">{}</a>', url, obj.partner.business_name)
    partner_link.short_description = 'Partner'

    def revenue_display(self, obj):
        """Display revenue."""
        return f"${obj.total_revenue:,.2f}"
    revenue_display.short_description = 'Revenue'
    revenue_display.admin_order_field = 'total_revenue'

    def acceptance_rate_display(self, obj):
        """Display acceptance rate with color."""
        rate = obj.acceptance_rate
        color = '#28a745' if rate >= 80 else '#ffc107' if rate >= 60 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    acceptance_rate_display.short_description = 'Acceptance'

    def completion_rate_display(self, obj):
        """Display completion rate with color."""
        rate = obj.completion_rate
        color = '#28a745' if rate >= 90 else '#ffc107' if rate >= 70 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    completion_rate_display.short_description = 'Completion'

    def rating_display(self, obj):
        """Display rating with stars."""
        if not obj.avg_rating:
            return '-'
        stars = '⭐' * int(obj.avg_rating)
        return format_html(
            '{} <span style="color: #6c757d;">({:.2f})</span>',
            stars, obj.avg_rating
        )
    rating_display.short_description = 'Rating'

    def issues_indicator(self, obj):
        """Show issues count with color."""
        total_issues = obj.issues_reported + obj.items_damaged + obj.items_lost
        if total_issues == 0:
            return format_html('<span style="color: #28a745;">{}</span>', '✓ No Issues')
        color = '#dc3545' if total_issues > 5 else '#ffc107'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} issues</span>',
            color, total_issues
        )
    issues_indicator.short_description = 'Issues'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('partner')


@admin.register(CustomerAnalytics)
class CustomerAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for Customer Analytics."""

    list_display = [
        'user_link',
        'lifetime_value_display',
        'segment_badge',
        'total_orders',
        'completed_orders',
        'avg_order_value_display',
        'churn_risk_display',
        'last_order_display',
    ]
    list_filter = [
        'customer_segment',
        'is_at_churn_risk',
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    fieldsets = [
        ('Customer', {
            'fields': ['id', 'user']
        }),
        ('Order Metrics', {
            'fields': [
                'total_orders',
                'completed_orders',
                'cancelled_orders',
            ]
        }),
        ('Revenue Metrics', {
            'fields': [
                'total_spent',
                'average_order_value',
                'lifetime_value',
            ]
        }),
        ('Engagement', {
            'fields': [
                'first_order_date',
                'last_order_date',
                'days_since_last_order',
                'order_frequency_days',
            ]
        }),
        ('Segmentation', {
            'fields': [
                'customer_segment',
                'favorite_service_category',
                'preferred_payment_method',
            ]
        }),
        ('Quality', {
            'fields': ['avg_rating_given']
        }),
        ('Churn Risk', {
            'fields': [
                'churn_risk_score',
                'is_at_churn_risk',
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    actions = ['update_customer_metrics']

    def user_link(self, obj):
        """Link to user."""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'

    def lifetime_value_display(self, obj):
        """Display LTV with currency."""
        return f"${obj.lifetime_value:,.2f}"
    lifetime_value_display.short_description = 'Lifetime Value'
    lifetime_value_display.admin_order_field = 'lifetime_value'

    def segment_badge(self, obj):
        """Display segment with colored badge."""
        colors = {
            'new': '#6c757d',
            'occasional': '#17a2b8',
            'regular': '#28a745',
            'vip': '#ffc107',
            'churned': '#dc3545',
        }
        color = colors.get(obj.customer_segment, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_customer_segment_display()
        )
    segment_badge.short_description = 'Segment'

    def avg_order_value_display(self, obj):
        """Display average order value."""
        return f"${obj.average_order_value:,.2f}"
    avg_order_value_display.short_description = 'Avg Order Value'

    def churn_risk_display(self, obj):
        """Display churn risk with color."""
        if obj.churn_risk_score >= 75:
            color = '#dc3545'
            label = 'High Risk'
        elif obj.churn_risk_score >= 50:
            color = '#ffc107'
            label = 'Medium Risk'
        else:
            color = '#28a745'
            label = 'Low Risk'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({:.0f})</span>',
            color, label, obj.churn_risk_score
        )
    churn_risk_display.short_description = 'Churn Risk'

    def last_order_display(self, obj):
        """Display last order info."""
        if not obj.last_order_date:
            return '-'
        return format_html(
            '{} <span style="color: #6c757d;">({} days ago)</span>',
            obj.last_order_date.strftime('%Y-%m-%d'),
            obj.days_since_last_order or 0
        )
    last_order_display.short_description = 'Last Order'

    def update_customer_metrics(self, request, queryset):
        """Action to update metrics for selected customers."""
        count = 0
        for customer in queryset:
            customer.update_metrics()
            count += 1
        self.message_user(request, f'Updated metrics for {count} customers.')
    update_customer_metrics.short_description = 'Update customer metrics'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    """Admin interface for Report Schedules."""

    list_display = [
        'name',
        'report_type_badge',
        'frequency_badge',
        'is_active',
        'last_run_display',
        'next_run_display',
        'created_by_link',
    ]
    list_filter = [
        'report_type',
        'frequency',
        'is_active',
        'created_at',
    ]
    search_fields = [
        'name',
        'description',
        'created_by__email',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    fieldsets = [
        ('Report Configuration', {
            'fields': [
                'id',
                'name',
                'description',
                'report_type',
            ]
        }),
        ('Schedule', {
            'fields': [
                'frequency',
                'day_of_week',
                'day_of_month',
                'time_of_day',
            ]
        }),
        ('Delivery', {
            'fields': [
                'email_to',
                'format',
            ]
        }),
        ('Filters', {
            'fields': ['filters'],
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': [
                'is_active',
                'last_run_at',
                'next_run_at',
            ]
        }),
        ('Created By', {
            'fields': ['created_by']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    actions = ['activate_reports', 'deactivate_reports']

    def report_type_badge(self, obj):
        """Display report type as badge."""
        return format_html(
            '<span style="background-color: #0d6efd; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            obj.get_report_type_display()
        )
    report_type_badge.short_description = 'Report Type'

    def frequency_badge(self, obj):
        """Display frequency as badge."""
        colors = {
            'daily': '#28a745',
            'weekly': '#17a2b8',
            'monthly': '#ffc107',
            'quarterly': '#6f42c1',
        }
        color = colors.get(obj.frequency, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_frequency_display()
        )
    frequency_badge.short_description = 'Frequency'

    def last_run_display(self, obj):
        """Display last run time."""
        if not obj.last_run_at:
            return format_html('<span style="color: #6c757d;">{}</span>', 'Never run')
        return obj.last_run_at.strftime('%Y-%m-%d %H:%M')
    last_run_display.short_description = 'Last Run'

    def next_run_display(self, obj):
        """Display next run time."""
        if not obj.next_run_at:
            return format_html('<span style="color: #6c757d;">{}</span>', 'Not scheduled')
        return obj.next_run_at.strftime('%Y-%m-%d %H:%M')
    next_run_display.short_description = 'Next Run'

    def created_by_link(self, obj):
        """Link to creator."""
        url = reverse('admin:accounts_user_change', args=[obj.created_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.created_by.email)
    created_by_link.short_description = 'Created By'

    def activate_reports(self, request, queryset):
        """Action to activate selected reports."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'Activated {count} reports.')
    activate_reports.short_description = 'Activate selected reports'

    def deactivate_reports(self, request, queryset):
        """Action to deactivate selected reports."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {count} reports.')
    deactivate_reports.short_description = 'Deactivate selected reports'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('created_by')


@admin.register(AnalyticsCache)
class AnalyticsCacheAdmin(admin.ModelAdmin):
    """Admin interface for Analytics Cache."""

    list_display = [
        'cache_key',
        'cache_type_badge',
        'expires_at',
        'is_expired_indicator',
        'created_at',
    ]
    list_filter = [
        'cache_type',
        'expires_at',
        'created_at',
    ]
    search_fields = ['cache_key']
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'is_expired',
    ]
    fieldsets = [
        ('Cache Info', {
            'fields': [
                'id',
                'cache_key',
                'cache_type',
            ]
        }),
        ('Data', {
            'fields': ['data']
        }),
        ('Expiry', {
            'fields': [
                'expires_at',
                'is_expired',
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    actions = ['clear_expired_cache']

    def cache_type_badge(self, obj):
        """Display cache type as badge."""
        return format_html(
            '<span style="background-color: #6f42c1; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            obj.get_cache_type_display()
        )
    cache_type_badge.short_description = 'Cache Type'

    def is_expired_indicator(self, obj):
        """Show if cache is expired."""
        if obj.is_expired:
            return format_html('<span style="color: #dc3545;">{}</span>', '✗ Expired')
        return format_html('<span style="color: #28a745;">{}</span>', '✓ Valid')
    is_expired_indicator.short_description = 'Status'
    is_expired_indicator.boolean = False

    def clear_expired_cache(self, request, queryset):
        """Action to clear expired cache entries."""
        from django.utils import timezone
        count = queryset.filter(expires_at__lt=timezone.now()).delete()[0]
        self.message_user(request, f'Cleared {count} expired cache entries.')
    clear_expired_cache.short_description = 'Clear expired cache'

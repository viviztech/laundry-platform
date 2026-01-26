"""
Analytics API views for business intelligence and reporting.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment, Refund
from apps.partners.models import Partner
from apps.accounts.models import User
from apps.orders.partner_models import OrderProcessingStage, OrderItemProcessing

from .models import (
    DailyRevenueSummary,
    PartnerPerformanceMetric,
    CustomerAnalytics,
    AnalyticsCache
)


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics API for business intelligence.

    Provides dashboard metrics, revenue analytics, order analytics,
    partner performance, and customer insights.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """
        Main dashboard with real-time metrics.

        GET /api/analytics/dashboard/
        """
        # Check cache first
        cache_key = 'dashboard_metrics'
        cached_data = AnalyticsCache.get_cached(cache_key)
        if cached_data:
            return Response(cached_data)

        today = timezone.now().date()
        now = timezone.now()

        # Today's metrics
        today_orders = Order.objects.filter(created_at__date=today)
        today_revenue = today_orders.filter(
            status='delivered'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # This week's metrics
        week_start = today - timedelta(days=today.weekday())
        week_orders = Order.objects.filter(created_at__date__gte=week_start)
        week_revenue = week_orders.filter(
            status='delivered'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # This month's metrics
        month_start = today.replace(day=1)
        month_orders = Order.objects.filter(created_at__date__gte=month_start)
        month_revenue = month_orders.filter(
            status='delivered'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # Order status distribution
        status_distribution = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        # Active users (ordered in last 30 days)
        thirty_days_ago = now - timedelta(days=30)
        active_users = User.objects.filter(
            orders__created_at__gte=thirty_days_ago
        ).distinct().count()

        # Active partners
        active_partners = Partner.objects.filter(
            is_verified=True,
            is_active=True
        ).count()

        # Pending orders requiring attention
        pending_orders = Order.objects.filter(
            status__in=['pending', 'confirmed']
        ).count()

        # Average order value
        avg_order_value = Order.objects.filter(
            status='delivered'
        ).aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')

        # Top performing partners (by revenue this month)
        top_partners = Partner.objects.filter(
            assigned_orders__created_at__date__gte=month_start,
            assigned_orders__status='delivered'
        ).annotate(
            revenue=Sum('assigned_orders__total_amount')
        ).order_by('-revenue')[:5]

        top_partners_data = [
            {
                'id': str(partner.id),
                'business_name': partner.business_name,
                'revenue': str(partner.revenue)
            }
            for partner in top_partners
        ]

        # Recent orders
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        recent_orders_data = [
            {
                'id': str(order.id),
                'order_number': order.order_number,
                'user': order.user.email,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.isoformat()
            }
            for order in recent_orders
        ]

        data = {
            'today': {
                'revenue': str(today_revenue),
                'orders': today_orders.count(),
                'completed': today_orders.filter(status='delivered').count(),
                'cancelled': today_orders.filter(status='cancelled').count(),
            },
            'week': {
                'revenue': str(week_revenue),
                'orders': week_orders.count(),
                'completed': week_orders.filter(status='delivered').count(),
            },
            'month': {
                'revenue': str(month_revenue),
                'orders': month_orders.count(),
                'completed': month_orders.filter(status='delivered').count(),
            },
            'metrics': {
                'average_order_value': str(avg_order_value),
                'active_users': active_users,
                'active_partners': active_partners,
                'pending_orders': pending_orders,
            },
            'order_status_distribution': list(status_distribution),
            'top_partners': top_partners_data,
            'recent_orders': recent_orders_data,
        }

        # Cache for 5 minutes
        AnalyticsCache.set_cached(cache_key, data, 'dashboard', ttl_minutes=5)

        return Response(data)

    @action(detail=False, methods=['get'], url_path='revenue')
    def revenue_analytics(self, request):
        """
        Revenue analytics with trends and breakdowns.

        GET /api/analytics/revenue/
        Query params:
        - period: day|week|month|year (default: month)
        - start_date: YYYY-MM-DD
        - end_date: YYYY-MM-DD
        """
        period = request.query_params.get('period', 'month')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Parse dates
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end = timezone.now().date()
            if period == 'day':
                start = end - timedelta(days=30)
            elif period == 'week':
                start = end - timedelta(weeks=12)
            elif period == 'year':
                start = end - timedelta(days=365)
            else:  # month
                start = end - timedelta(days=90)

        # Get orders in date range
        orders = Order.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end,
            status='delivered'
        )

        # Total revenue
        total_revenue = orders.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')

        # Revenue by payment method
        payment_breakdown = orders.values('payment_method').annotate(
            revenue=Sum('total_amount'),
            count=Count('id')
        ).order_by('-revenue')

        # Revenue by service category
        service_breakdown = OrderItem.objects.filter(
            order__in=orders
        ).values('service__category').annotate(
            revenue=Sum('total_price'),
            count=Count('id')
        ).order_by('-revenue')

        # Daily revenue trend
        daily_summaries = DailyRevenueSummary.objects.filter(
            date__gte=start,
            date__lte=end
        ).order_by('date')

        daily_trend = [
            {
                'date': summary.date.isoformat(),
                'revenue': str(summary.total_revenue),
                'orders': summary.order_count,
                'avg_order_value': str(summary.average_order_value)
            }
            for summary in daily_summaries
        ]

        # Refunds
        refunds = Refund.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end,
            status='completed'
        )
        total_refunds = refunds.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        # Net revenue
        net_revenue = total_revenue - total_refunds

        data = {
            'period': {
                'start': start.isoformat(),
                'end': end.isoformat(),
            },
            'summary': {
                'total_revenue': str(total_revenue),
                'total_refunds': str(total_refunds),
                'net_revenue': str(net_revenue),
                'order_count': orders.count(),
                'average_order_value': str(total_revenue / orders.count() if orders.count() > 0 else 0),
            },
            'payment_method_breakdown': [
                {
                    'method': item['payment_method'],
                    'revenue': str(item['revenue']),
                    'count': item['count'],
                    'percentage': float((item['revenue'] / total_revenue * 100) if total_revenue > 0 else 0)
                }
                for item in payment_breakdown
            ],
            'service_category_breakdown': [
                {
                    'category': item['service__category'],
                    'revenue': str(item['revenue']),
                    'count': item['count']
                }
                for item in service_breakdown
            ],
            'daily_trend': daily_trend,
        }

        return Response(data)

    @action(detail=False, methods=['get'], url_path='orders')
    def order_analytics(self, request):
        """
        Order analytics with volume, status, and timing metrics.

        GET /api/analytics/orders/
        Query params:
        - period: day|week|month|year (default: month)
        - start_date: YYYY-MM-DD
        - end_date: YYYY-MM-DD
        """
        period = request.query_params.get('period', 'month')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Parse dates
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end = timezone.now().date()
            if period == 'day':
                start = end - timedelta(days=30)
            elif period == 'week':
                start = end - timedelta(weeks=12)
            elif period == 'year':
                start = end - timedelta(days=365)
            else:  # month
                start = end - timedelta(days=90)

        # Get orders in date range
        orders = Order.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end
        )

        # Status distribution
        status_distribution = orders.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        # Completion rate
        total_orders = orders.count()
        completed_orders = orders.filter(status='delivered').count()
        cancelled_orders = orders.filter(status='cancelled').count()
        completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0

        # Average fulfillment time (from created to completed)
        completed = orders.filter(
            status='delivered',
            completed_at__isnull=False
        )
        fulfillment_times = []
        for order in completed:
            if order.completed_at and order.created_at:
                duration = (order.completed_at - order.created_at).total_seconds() / 3600  # hours
                fulfillment_times.append(duration)

        avg_fulfillment_time = sum(fulfillment_times) / len(fulfillment_times) if fulfillment_times else 0

        # Peak hours analysis
        hourly_distribution = orders.extra(
            select={'hour': 'EXTRACT(hour FROM created_at)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        # Day of week distribution
        dow_distribution = orders.extra(
            select={'dow': 'EXTRACT(dow FROM created_at)'}
        ).values('dow').annotate(
            count=Count('id')
        ).order_by('dow')

        data = {
            'period': {
                'start': start.isoformat(),
                'end': end.isoformat(),
            },
            'summary': {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'completion_rate': round(completion_rate, 2),
                'cancellation_rate': round(cancellation_rate, 2),
                'avg_fulfillment_time_hours': round(avg_fulfillment_time, 2),
            },
            'status_distribution': list(status_distribution),
            'hourly_distribution': list(hourly_distribution),
            'day_of_week_distribution': list(dow_distribution),
        }

        return Response(data)

    @action(detail=False, methods=['get'], url_path='partners')
    def partner_analytics(self, request):
        """
        Partner performance analytics.

        GET /api/analytics/partners/
        Query params:
        - partner_id: UUID (optional, for specific partner)
        - start_date: YYYY-MM-DD
        - end_date: YYYY-MM-DD
        """
        partner_id = request.query_params.get('partner_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Parse dates
        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end = timezone.now().date()
            start = end - timedelta(days=30)

        # Get metrics
        metrics_query = PartnerPerformanceMetric.objects.filter(
            date__gte=start,
            date__lte=end
        )

        if partner_id:
            metrics_query = metrics_query.filter(partner_id=partner_id)

        # Aggregate metrics
        aggregated = metrics_query.aggregate(
            total_orders_received=Sum('orders_received'),
            total_orders_accepted=Sum('orders_accepted'),
            total_orders_rejected=Sum('orders_rejected'),
            total_orders_completed=Sum('orders_completed'),
            total_revenue=Sum('total_revenue'),
            avg_rating=Avg('avg_rating'),
            total_issues=Sum('issues_reported'),
            total_items_damaged=Sum('items_damaged'),
            total_items_lost=Sum('items_lost'),
        )

        # Calculate rates
        total_received = aggregated['total_orders_received'] or 0
        acceptance_rate = (aggregated['total_orders_accepted'] / total_received * 100) if total_received > 0 else 0
        rejection_rate = (aggregated['total_orders_rejected'] / total_received * 100) if total_received > 0 else 0

        total_accepted = aggregated['total_orders_accepted'] or 0
        completion_rate = (aggregated['total_orders_completed'] / total_accepted * 100) if total_accepted > 0 else 0

        # Top performing partners
        top_partners = Partner.objects.filter(
            performance_metrics__date__gte=start,
            performance_metrics__date__lte=end
        ).annotate(
            total_revenue=Sum('performance_metrics__total_revenue'),
            total_completed=Sum('performance_metrics__orders_completed'),
            avg_rating=Avg('performance_metrics__avg_rating')
        ).order_by('-total_revenue')[:10]

        top_partners_data = [
            {
                'id': str(partner.id),
                'business_name': partner.business_name,
                'revenue': str(partner.total_revenue or 0),
                'completed_orders': partner.total_completed or 0,
                'avg_rating': str(round(partner.avg_rating, 2)) if partner.avg_rating else None,
            }
            for partner in top_partners
        ]

        # Processing stage metrics
        stage_durations = OrderProcessingStage.objects.filter(
            started_at__date__gte=start,
            started_at__date__lte=end,
            completed_at__isnull=False
        ).values('stage').annotate(
            avg_duration=Avg('duration_minutes'),
            count=Count('id')
        ).order_by('-count')

        data = {
            'period': {
                'start': start.isoformat(),
                'end': end.isoformat(),
            },
            'summary': {
                'total_orders_received': aggregated['total_orders_received'] or 0,
                'total_orders_accepted': aggregated['total_orders_accepted'] or 0,
                'total_orders_completed': aggregated['total_orders_completed'] or 0,
                'total_revenue': str(aggregated['total_revenue'] or 0),
                'acceptance_rate': round(acceptance_rate, 2),
                'rejection_rate': round(rejection_rate, 2),
                'completion_rate': round(completion_rate, 2),
                'avg_rating': str(round(aggregated['avg_rating'], 2)) if aggregated['avg_rating'] else None,
                'total_issues': aggregated['total_issues'] or 0,
                'total_items_damaged': aggregated['total_items_damaged'] or 0,
                'total_items_lost': aggregated['total_items_lost'] or 0,
            },
            'top_partners': top_partners_data,
            'processing_stage_metrics': [
                {
                    'stage': item['stage'],
                    'avg_duration_minutes': round(item['avg_duration'], 2) if item['avg_duration'] else 0,
                    'count': item['count']
                }
                for item in stage_durations
            ],
        }

        # If specific partner requested, add detailed metrics
        if partner_id:
            partner_metrics = metrics_query.order_by('date')
            data['daily_metrics'] = [
                {
                    'date': metric.date.isoformat(),
                    'orders_received': metric.orders_received,
                    'orders_completed': metric.orders_completed,
                    'revenue': str(metric.total_revenue),
                    'avg_rating': str(metric.avg_rating) if metric.avg_rating else None,
                }
                for metric in partner_metrics
            ]

        return Response(data)

    @action(detail=False, methods=['get'], url_path='customers')
    def customer_analytics(self, request):
        """
        Customer analytics with segmentation and insights.

        GET /api/analytics/customers/
        Query params:
        - segment: new|occasional|regular|vip|churned (optional)
        - at_risk: true|false (optional)
        """
        segment = request.query_params.get('segment')
        at_risk = request.query_params.get('at_risk')

        # Base query
        customers = CustomerAnalytics.objects.all()

        if segment:
            customers = customers.filter(customer_segment=segment)

        if at_risk == 'true':
            customers = customers.filter(is_at_churn_risk=True)

        # Summary statistics
        total_customers = customers.count()
        total_ltv = customers.aggregate(
            total=Sum('lifetime_value')
        )['total'] or Decimal('0.00')

        avg_ltv = customers.aggregate(
            avg=Avg('lifetime_value')
        )['avg'] or Decimal('0.00')

        # Segment distribution
        segment_distribution = CustomerAnalytics.objects.values(
            'customer_segment'
        ).annotate(
            count=Count('id'),
            total_ltv=Sum('lifetime_value')
        ).order_by('-count')

        # Churn risk distribution
        churn_risk_high = CustomerAnalytics.objects.filter(
            churn_risk_score__gte=75
        ).count()
        churn_risk_medium = CustomerAnalytics.objects.filter(
            churn_risk_score__gte=50,
            churn_risk_score__lt=75
        ).count()
        churn_risk_low = CustomerAnalytics.objects.filter(
            churn_risk_score__lt=50
        ).count()

        # Top customers by LTV
        top_customers = customers.order_by('-lifetime_value')[:20]
        top_customers_data = [
            {
                'id': str(customer.user.id),
                'email': customer.user.email,
                'lifetime_value': str(customer.lifetime_value),
                'total_orders': customer.total_orders,
                'segment': customer.customer_segment,
            }
            for customer in top_customers
        ]

        # At-risk customers
        at_risk_customers = CustomerAnalytics.objects.filter(
            is_at_churn_risk=True
        ).order_by('-lifetime_value')[:20]
        at_risk_data = [
            {
                'id': str(customer.user.id),
                'email': customer.user.email,
                'lifetime_value': str(customer.lifetime_value),
                'days_since_last_order': customer.days_since_last_order,
                'churn_risk_score': str(customer.churn_risk_score),
            }
            for customer in at_risk_customers
        ]

        data = {
            'summary': {
                'total_customers': total_customers,
                'total_lifetime_value': str(total_ltv),
                'average_lifetime_value': str(avg_ltv),
            },
            'segment_distribution': [
                {
                    'segment': item['customer_segment'],
                    'count': item['count'],
                    'total_ltv': str(item['total_ltv'] or 0),
                }
                for item in segment_distribution
            ],
            'churn_risk': {
                'high': churn_risk_high,
                'medium': churn_risk_medium,
                'low': churn_risk_low,
            },
            'top_customers': top_customers_data,
            'at_risk_customers': at_risk_data,
        }

        return Response(data)

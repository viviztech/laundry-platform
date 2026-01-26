"""
Admin configuration for orders app.
"""

from django.contrib import admin
from .models import Order, OrderItem, OrderAddon, OrderStatusHistory, OrderRating


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price', 'created_at')
    fields = ('service', 'quantity', 'unit_price', 'total_price', 'notes')


class OrderAddonInline(admin.TabularInline):
    """Inline admin for order addons."""
    model = OrderAddon
    extra = 0
    readonly_fields = ('total_price', 'created_at')
    fields = ('addon', 'order_item', 'quantity', 'unit_price', 'total_price')


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline admin for order status history."""
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'changed_at')
    fields = ('old_status', 'new_status', 'changed_by', 'notes', 'changed_at')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""

    list_display = (
        'order_number', 'user', 'status', 'payment_status',
        'total_amount', 'pickup_date', 'created_at'
    )
    list_filter = (
        'status', 'payment_status', 'payment_method',
        'pickup_date', 'created_at'
    )
    search_fields = (
        'order_number', 'user__email', 'user__first_name',
        'user__last_name', 'payment_id'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'order_number', 'created_at', 'updated_at',
        'confirmed_at', 'completed_at'
    )

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Addresses', {
            'fields': ('pickup_address', 'delivery_address')
        }),
        ('Schedule', {
            'fields': (
                'pickup_date', 'pickup_time_slot',
                'delivery_date', 'delivery_time_slot'
            )
        }),
        ('Pricing', {
            'fields': (
                'subtotal', 'tax_amount', 'delivery_fee',
                'discount_amount', 'total_amount'
            )
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_method', 'payment_id')
        }),
        ('Additional Information', {
            'fields': (
                'special_instructions', 'customer_notes',
                'internal_notes', 'assigned_partner_id'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at',
                'confirmed_at', 'completed_at'
            )
        }),
    )

    inlines = [OrderItemInline, OrderAddonInline, OrderStatusHistoryInline]
    list_select_related = ('user', 'pickup_address')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model."""

    list_display = ('order', 'service', 'quantity', 'unit_price', 'total_price', 'created_at')
    list_filter = ('service__category', 'created_at')
    search_fields = ('order__order_number', 'service__name')
    ordering = ('-created_at',)
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    list_select_related = ('order', 'service')


@admin.register(OrderAddon)
class OrderAddonAdmin(admin.ModelAdmin):
    """Admin configuration for OrderAddon model."""

    list_display = ('order', 'addon', 'order_item', 'quantity', 'unit_price', 'total_price', 'created_at')
    list_filter = ('addon', 'created_at')
    search_fields = ('order__order_number', 'addon__name')
    ordering = ('-created_at',)
    readonly_fields = ('total_price', 'created_at')
    list_select_related = ('order', 'addon', 'order_item')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for OrderStatusHistory model."""

    list_display = ('order', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = ('order__order_number', 'notes')
    ordering = ('-changed_at',)
    readonly_fields = ('changed_at',)
    list_select_related = ('order', 'changed_by')


@admin.register(OrderRating)
class OrderRatingAdmin(admin.ModelAdmin):
    """Admin configuration for OrderRating model."""

    list_display = (
        'order', 'user', 'overall_rating',
        'service_rating', 'delivery_rating',
        'is_published', 'created_at'
    )
    list_filter = (
        'overall_rating', 'service_rating', 'delivery_rating',
        'is_published', 'created_at'
    )
    search_fields = ('order__order_number', 'user__email', 'review')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('order', 'user')


# Import partner admin classes
from .partner_admin import (
    OrderProcessingStageAdmin,
    OrderItemProcessingAdmin,
    PartnerOrderNoteAdmin,
    DeliveryProofAdmin
)

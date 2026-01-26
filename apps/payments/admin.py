"""
Admin configuration for payments app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, Wallet, WalletTransaction, Refund, PaymentMethod


class WalletTransactionInline(admin.TabularInline):
    """Inline admin for wallet transactions."""
    model = WalletTransaction
    extra = 0
    fields = ('transaction_id', 'transaction_type', 'amount', 'balance_after', 'description', 'created_at')
    readonly_fields = ('transaction_id', 'balance_after', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""

    list_display = (
        'payment_id', 'order', 'user', 'amount', 'method',
        'gateway', 'status', 'created_at'
    )
    list_filter = (
        'status', 'method', 'gateway', 'created_at'
    )
    search_fields = (
        'payment_id', 'order__order_id', 'user__email',
        'gateway_payment_id', 'gateway_order_id'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'payment_id', 'net_amount', 'created_at', 'updated_at'
    )

    fieldsets = (
        ('Payment Information', {
            'fields': (
                'payment_id', 'order', 'user', 'amount', 'transaction_fee',
                'net_amount', 'currency'
            )
        }),
        ('Payment Method', {
            'fields': ('method',)
        }),
        ('Gateway Information', {
            'fields': (
                'gateway', 'gateway_payment_id', 'gateway_order_id',
                'gateway_signature'
            )
        }),
        ('Status', {
            'fields': ('status', 'failure_reason')
        }),
        ('Additional Information', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    list_select_related = ('order', 'user')

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation."""
        readonly = list(self.readonly_fields)
        if obj:  # Editing an existing object
            readonly.extend(['order', 'user', 'amount', 'gateway'])
        return readonly


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Admin configuration for Wallet model."""

    list_display = (
        'user', 'balance', 'is_active', 'updated_at'
    )
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-balance',)
    readonly_fields = ('balance', 'created_at', 'updated_at')

    fieldsets = (
        ('Wallet Information', {
            'fields': ('user', 'balance', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    inlines = [WalletTransactionInline]
    list_select_related = ('user',)

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation."""
        readonly = list(self.readonly_fields)
        if obj:  # Editing an existing object
            readonly.append('user')
        return readonly


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """Admin configuration for WalletTransaction model."""

    list_display = (
        'transaction_id', 'wallet', 'transaction_type', 'amount',
        'balance_after', 'created_at'
    )
    list_filter = ('transaction_type', 'created_at')
    search_fields = (
        'transaction_id', 'wallet__user__email', 'description',
        'payment__payment_id', 'order__order_id'
    )
    ordering = ('-created_at',)
    readonly_fields = ('transaction_id', 'balance_after', 'created_at')

    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'transaction_id', 'wallet', 'transaction_type',
                'amount', 'balance_after'
            )
        }),
        ('Related Objects', {
            'fields': ('payment', 'order', 'refund')
        }),
        ('Description', {
            'fields': ('description', 'metadata')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

    list_select_related = ('wallet__user', 'payment', 'order', 'refund')

    def has_add_permission(self, request):
        """Prevent manual creation of wallet transactions."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of wallet transactions."""
        return False


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin configuration for Refund model."""

    list_display = (
        'refund_id', 'payment', 'amount', 'reason',
        'status', 'user', 'created_at'
    )
    list_filter = ('status', 'reason', 'created_at', 'processed_at')
    search_fields = (
        'refund_id', 'payment__payment_id', 'payment__order__order_id',
        'user__email', 'gateway_refund_id'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'refund_id', 'created_at', 'updated_at',
        'processed_at', 'completed_at'
    )

    fieldsets = (
        ('Refund Information', {
            'fields': (
                'refund_id', 'payment', 'amount', 'reason'
            )
        }),
        ('Request Information', {
            'fields': ('user', 'description')
        }),
        ('Status', {
            'fields': (
                'status', 'processed_at', 'processed_by',
                'completed_at', 'error_message'
            )
        }),
        ('Gateway Information', {
            'fields': ('gateway_refund_id',)
        }),
        ('Additional Information', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    list_select_related = (
        'payment__order', 'user', 'processed_by'
    )

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation."""
        readonly = list(self.readonly_fields)
        if obj:  # Editing an existing object
            readonly.extend(['payment', 'amount', 'reason', 'user'])
        return readonly


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentMethod model."""

    list_display = (
        'user', 'type', 'nickname', 'is_default',
        'is_active', 'created_at'
    )
    list_filter = ('type', 'is_default', 'is_active', 'created_at')
    search_fields = (
        'user__email', 'nickname', 'card_last4', 'upi_id'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Payment Method Information', {
            'fields': (
                'user', 'type', 'nickname',
                'is_default', 'is_active'
            )
        }),
        ('Card Details', {
            'fields': ('card_last4', 'card_brand', 'card_expiry_month', 'card_expiry_year'),
            'classes': ('collapse',)
        }),
        ('UPI Details', {
            'fields': ('upi_id',),
            'classes': ('collapse',)
        }),
        ('Gateway Information', {
            'fields': ('gateway_token',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    list_select_related = ('user',)

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation."""
        readonly = list(self.readonly_fields)
        if obj:  # Editing an existing object
            readonly.extend(['user', 'type'])
        return readonly

    def save_model(self, request, obj, form, change):
        """Ensure only one default payment method per user."""
        if obj.is_default:
            # Unset default for other payment methods of this user
            PaymentMethod.objects.filter(
                user=obj.user, is_default=True
            ).exclude(id=obj.id).update(is_default=False)
        super().save_model(request, obj, form, change)

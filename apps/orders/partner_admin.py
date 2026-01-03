"""
Django admin configuration for Partner Order Processing models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .partner_models import (
    OrderProcessingStage,
    OrderItemProcessing,
    PartnerOrderNote,
    DeliveryProof
)


@admin.register(OrderProcessingStage)
class OrderProcessingStageAdmin(admin.ModelAdmin):
    """Admin interface for Order Processing Stages."""

    list_display = [
        'order_link',
        'stage_badge',
        'category_badge',
        'performed_by_link',
        'started_at',
        'completed_at',
        'duration_minutes',
        'issue_indicator',
    ]
    list_filter = [
        'stage',
        'stage_category',
        'has_issue',
        'issue_resolved',
        'started_at',
    ]
    search_fields = [
        'order__order_number',
        'notes',
        'issue_description',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    fieldsets = [
        ('Stage Information', {
            'fields': ['id', 'order', 'stage', 'stage_category', 'performed_by']
        }),
        ('Timing', {
            'fields': ['started_at', 'completed_at', 'duration_minutes']
        }),
        ('Details', {
            'fields': ['notes', 'photos', 'metadata']
        }),
        ('Issues', {
            'fields': ['has_issue', 'issue_description', 'issue_resolved']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    date_hierarchy = 'started_at'

    def order_link(self, obj):
        """Link to order."""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

    def stage_badge(self, obj):
        """Display stage as badge."""
        colors = {
            'assignment': '#6c757d',
            'pickup': '#0dcaf0',
            'inspection': '#ffc107',
            'processing': '#0d6efd',
            'finishing': '#198754',
            'delivery': '#20c997',
            'issue': '#dc3545',
        }
        color = colors.get(obj.stage_category, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_stage_display()
        )
    stage_badge.short_description = 'Stage'

    def category_badge(self, obj):
        """Display category as badge."""
        return format_html(
            '<span style="background-color: #e9ecef; padding: 2px 6px; border-radius: 2px; font-size: 11px;">{}</span>',
            obj.get_stage_category_display()
        )
    category_badge.short_description = 'Category'

    def performed_by_link(self, obj):
        """Link to performer."""
        if obj.performed_by:
            url = reverse('admin:accounts_user_change', args=[obj.performed_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.performed_by.email)
        return '-'
    performed_by_link.short_description = 'Performed By'

    def issue_indicator(self, obj):
        """Show issue status."""
        if obj.has_issue:
            if obj.issue_resolved:
                return format_html('<span style="color: green;">✓ Resolved</span>')
            return format_html('<span style="color: red;">⚠ Issue</span>')
        return '-'
    issue_indicator.short_description = 'Issue'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'performed_by')


@admin.register(OrderItemProcessing)
class OrderItemProcessingAdmin(admin.ModelAdmin):
    """Admin interface for Order Item Processing."""

    list_display = [
        'order_item_link',
        'status_badge',
        'condition_indicator',
        'stain_indicator',
        'damage_indicator',
        'additional_charges',
        'quality_score',
        'processing_time',
    ]
    list_filter = [
        'status',
        'initial_condition',
        'has_stains',
        'has_damage',
        'requires_special_care',
        'created_at',
    ]
    search_fields = [
        'order_item__order__order_number',
        'processing_notes',
        'stain_details',
        'damage_details',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'processing_time_display',
    ]
    fieldsets = [
        ('Item Information', {
            'fields': ['id', 'order_item', 'status', 'processed_by']
        }),
        ('Condition', {
            'fields': ['initial_condition', 'final_condition']
        }),
        ('Issues', {
            'fields': [
                'has_stains', 'stain_details', 'stain_photos',
                'has_damage', 'damage_details', 'damage_photos',
                'requires_special_care', 'special_care_notes'
            ]
        }),
        ('Processing Details', {
            'fields': [
                'washing_temp', 'detergent_type',
                'drying_method', 'ironing_temp'
            ]
        }),
        ('Timeline', {
            'fields': [
                'inspection_at',
                'washing_started_at', 'washing_completed_at',
                'drying_started_at', 'drying_completed_at',
                'ironing_started_at', 'ironing_completed_at',
                'completed_at', 'processing_time_display'
            ]
        }),
        ('Quality & Charges', {
            'fields': [
                'quality_score', 'quality_notes',
                'additional_charges', 'additional_charges_reason'
            ]
        }),
        ('Notes', {
            'fields': ['processing_notes']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    date_hierarchy = 'created_at'

    def order_item_link(self, obj):
        """Link to order item."""
        return format_html(
            '<a href="{}">{} - {}</a>',
            reverse('admin:orders_orderitem_change', args=[obj.order_item.id]),
            obj.order_item.order.order_number,
            obj.order_item
        )
    order_item_link.short_description = 'Order Item'

    def status_badge(self, obj):
        """Display status as badge."""
        colors = {
            'pending': '#6c757d',
            'inspecting': '#ffc107',
            'stain_treating': '#fd7e14',
            'washing': '#0d6efd',
            'drying': '#17a2b8',
            'ironing': '#6f42c1',
            'quality_check': '#20c997',
            'packaged': '#198754',
            'completed': '#28a745',
            'damaged': '#dc3545',
            'lost': '#000',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def condition_indicator(self, obj):
        """Show condition."""
        if obj.final_condition:
            condition = obj.final_condition
        else:
            condition = obj.initial_condition

        colors = {
            'excellent': 'green',
            'good': '#28a745',
            'fair': 'orange',
            'poor': 'red',
            'missing': 'black',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(condition, 'gray'),
            obj.get_initial_condition_display() if not obj.final_condition else obj.get_final_condition_display()
        )
    condition_indicator.short_description = 'Condition'

    def stain_indicator(self, obj):
        """Show stain status."""
        if obj.has_stains:
            return format_html('<span style="color: orange;">⚠ Stains</span>')
        return '-'
    stain_indicator.short_description = 'Stains'

    def damage_indicator(self, obj):
        """Show damage status."""
        if obj.has_damage:
            return format_html('<span style="color: red;">⚠ Damage</span>')
        return '-'
    damage_indicator.short_description = 'Damage'

    def processing_time(self, obj):
        """Show processing time."""
        time = obj.calculate_processing_time()
        if time:
            return f"{time} hours"
        return '-'
    processing_time.short_description = 'Time'

    def processing_time_display(self, obj):
        """Formatted processing time."""
        time = obj.calculate_processing_time()
        if time:
            return f"{time} hours"
        return 'Not completed'
    processing_time_display.short_description = 'Processing Time'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('order_item__order', 'processed_by')


@admin.register(PartnerOrderNote)
class PartnerOrderNoteAdmin(admin.ModelAdmin):
    """Admin interface for Partner Order Notes."""

    list_display = [
        'order_link',
        'note_type_badge',
        'content_preview',
        'urgent_indicator',
        'resolved_indicator',
        'created_by_link',
        'created_at',
    ]
    list_filter = [
        'note_type',
        'is_urgent',
        'is_resolved',
        'created_at',
    ]
    search_fields = [
        'order__order_number',
        'content',
        'created_by__email',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    fieldsets = [
        ('Note Information', {
            'fields': ['id', 'order', 'note_type', 'content']
        }),
        ('Status', {
            'fields': ['is_urgent', 'is_resolved']
        }),
        ('Attachments', {
            'fields': ['attachments']
        }),
        ('Author', {
            'fields': ['created_by', 'created_at', 'updated_at']
        }),
    ]
    date_hierarchy = 'created_at'

    def order_link(self, obj):
        """Link to order."""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

    def note_type_badge(self, obj):
        """Display note type as badge."""
        colors = {
            'general': '#6c757d',
            'issue': '#dc3545',
            'customer_request': '#0d6efd',
            'internal': '#ffc107',
            'quality': '#fd7e14',
        }
        color = colors.get(obj.note_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 2px; font-size: 11px;">{}</span>',
            color,
            obj.get_note_type_display()
        )
    note_type_badge.short_description = 'Type'

    def content_preview(self, obj):
        """Preview content."""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    def urgent_indicator(self, obj):
        """Show urgent status."""
        if obj.is_urgent:
            return format_html('<span style="color: red;">🔴 Urgent</span>')
        return '-'
    urgent_indicator.short_description = 'Urgent'

    def resolved_indicator(self, obj):
        """Show resolved status."""
        if obj.is_resolved:
            return format_html('<span style="color: green;">✓ Resolved</span>')
        return '-'
    resolved_indicator.short_description = 'Resolved'

    def created_by_link(self, obj):
        """Link to creator."""
        url = reverse('admin:accounts_user_change', args=[obj.created_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.created_by.email)
    created_by_link.short_description = 'Created By'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'created_by')


@admin.register(DeliveryProof)
class DeliveryProofAdmin(admin.ModelAdmin):
    """Admin interface for Delivery Proof."""

    list_display = [
        'order_link',
        'delivered_to',
        'delivered_to_relation',
        'has_signature',
        'photo_count',
        'delivered_by_link',
        'delivered_at',
    ]
    list_filter = [
        'delivered_at',
        'delivered_to_relation',
    ]
    search_fields = [
        'order__order_number',
        'delivered_to',
        'signature_name',
        'delivery_notes',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'signature_preview',
        'location_display',
    ]
    fieldsets = [
        ('Order Information', {
            'fields': ['id', 'order', 'delivered_at']
        }),
        ('Recipient', {
            'fields': ['delivered_to', 'delivered_to_relation']
        }),
        ('Photos', {
            'fields': ['package_photos', 'delivery_location_photo', 'photo_count_display']
        }),
        ('Signature', {
            'fields': ['customer_signature', 'signature_preview', 'signature_name']
        }),
        ('Location', {
            'fields': ['delivery_latitude', 'delivery_longitude', 'location_display']
        }),
        ('Notes', {
            'fields': ['delivery_notes']
        }),
        ('Delivered By', {
            'fields': ['delivered_by', 'created_at']
        }),
    ]
    date_hierarchy = 'delivered_at'

    def order_link(self, obj):
        """Link to order."""
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'

    def has_signature(self, obj):
        """Check if signature exists."""
        if obj.customer_signature:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_signature.short_description = 'Signature'

    def photo_count(self, obj):
        """Count photos."""
        return len(obj.package_photos) if obj.package_photos else 0
    photo_count.short_description = 'Photos'

    def photo_count_display(self, obj):
        """Display photo count."""
        count = len(obj.package_photos) if obj.package_photos else 0
        return f"{count} photo(s)"
    photo_count_display.short_description = 'Photo Count'

    def delivered_by_link(self, obj):
        """Link to delivery person."""
        if obj.delivered_by:
            url = reverse('admin:accounts_user_change', args=[obj.delivered_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.delivered_by.email)
        return '-'
    delivered_by_link.short_description = 'Delivered By'

    def signature_preview(self, obj):
        """Preview signature."""
        if obj.customer_signature:
            if obj.customer_signature.startswith('http'):
                return format_html('<img src="{}" style="max-width: 200px;" />', obj.customer_signature)
            return 'Signature data available'
        return 'No signature'
    signature_preview.short_description = 'Signature Preview'

    def location_display(self, obj):
        """Display location as Google Maps link."""
        if obj.delivery_latitude and obj.delivery_longitude:
            url = f"https://www.google.com/maps?q={obj.delivery_latitude},{obj.delivery_longitude}"
            return format_html('<a href="{}" target="_blank">View on Google Maps</a>', url)
        return 'No location data'
    location_display.short_description = 'Location'

    def get_queryset(self, request):
        """Optimize queryset."""
        qs = super().get_queryset(request)
        return qs.select_related('order', 'delivered_by')

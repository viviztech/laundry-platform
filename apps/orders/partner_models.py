"""
Partner-specific order processing models.

This module handles the detailed workflow stages that partners
go through when processing laundry orders.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

from .models import Order, OrderItem


class OrderProcessingStage(models.Model):
    """
    Detailed processing stages for partner workflow.

    Tracks each stage of the laundry process from pickup to delivery:
    - Order Assignment & Acceptance
    - Pickup
    - Inspection & Quality Check
    - Stain Treatment
    - Washing
    - Drying
    - Ironing/Pressing
    - Quality Control
    - Packaging
    - Out for Delivery
    - Delivered
    """

    STAGE_CHOICES = [
        # Assignment
        ('assigned', 'Assigned to Partner'),
        ('accepted', 'Accepted by Partner'),
        ('rejected', 'Rejected by Partner'),

        # Pickup
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('out_for_pickup', 'Out for Pickup'),
        ('pickup_completed', 'Pickup Completed'),

        # Inspection
        ('inspection', 'Quality Inspection'),
        ('inspection_complete', 'Inspection Complete'),

        # Processing
        ('stain_treatment', 'Stain Treatment'),
        ('washing', 'Washing'),
        ('drying', 'Drying'),
        ('ironing', 'Ironing/Pressing'),
        ('steam_pressing', 'Steam Pressing'),

        # Quality & Packaging
        ('quality_check', 'Quality Control Check'),
        ('packaging', 'Packaging'),
        ('ready_for_delivery', 'Ready for Delivery'),

        # Delivery
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered to Customer'),

        # Issues
        ('on_hold', 'On Hold'),
        ('issue_reported', 'Issue Reported'),
    ]

    STAGE_CATEGORY = [
        ('assignment', 'Assignment'),
        ('pickup', 'Pickup'),
        ('inspection', 'Inspection'),
        ('processing', 'Processing'),
        ('finishing', 'Finishing'),
        ('delivery', 'Delivery'),
        ('issue', 'Issue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='processing_stages'
    )

    stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    stage_category = models.CharField(max_length=20, choices=STAGE_CATEGORY)

    # Staff who performed this stage
    performed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_stages'
    )

    # Timing
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)

    # Details
    notes = models.TextField(blank=True)
    photos = models.JSONField(default=list, blank=True)  # Array of photo URLs
    metadata = models.JSONField(default=dict, blank=True)

    # Issues
    has_issue = models.BooleanField(default=False)
    issue_description = models.TextField(blank=True)
    issue_resolved = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_processing_stages'
        verbose_name = 'Order Processing Stage'
        verbose_name_plural = 'Order Processing Stages'
        ordering = ['started_at']
        indexes = [
            models.Index(fields=['order', 'stage']),
            models.Index(fields=['order', 'started_at']),
            models.Index(fields=['stage', 'created_at']),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.get_stage_display()}"

    def complete_stage(self):
        """Mark stage as complete and calculate duration."""
        self.completed_at = timezone.now()
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 60
            self.duration_minutes = int(duration)
        self.save()


class OrderItemProcessing(models.Model):
    """
    Item-level processing tracking.

    Tracks each individual item through the laundry process,
    allowing partners to mark progress on specific garments.
    """

    ITEM_STATUS = [
        ('pending', 'Pending'),
        ('inspecting', 'Under Inspection'),
        ('stain_treating', 'Stain Treatment'),
        ('washing', 'Washing'),
        ('drying', 'Drying'),
        ('ironing', 'Ironing'),
        ('quality_check', 'Quality Check'),
        ('packaged', 'Packaged'),
        ('completed', 'Completed'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
    ]

    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair - Minor Issues'),
        ('poor', 'Poor - Damaged'),
        ('missing', 'Missing/Lost'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='processing_details'
    )

    # Current status
    status = models.CharField(max_length=20, choices=ITEM_STATUS, default='pending')

    # Inspection details
    initial_condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='good'
    )
    final_condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        null=True,
        blank=True
    )

    # Stain/Damage tracking
    has_stains = models.BooleanField(default=False)
    stain_details = models.TextField(blank=True)
    stain_photos = models.JSONField(default=list, blank=True)

    has_damage = models.BooleanField(default=False)
    damage_details = models.TextField(blank=True)
    damage_photos = models.JSONField(default=list, blank=True)

    # Special care
    requires_special_care = models.BooleanField(default=False)
    special_care_notes = models.TextField(blank=True)

    # Processing details
    washing_temp = models.CharField(max_length=20, blank=True)  # cold, warm, hot
    detergent_type = models.CharField(max_length=50, blank=True)
    drying_method = models.CharField(max_length=20, blank=True)  # air, tumble, hang
    ironing_temp = models.CharField(max_length=20, blank=True)  # low, medium, high

    # Timing
    inspection_at = models.DateTimeField(null=True, blank=True)
    washing_started_at = models.DateTimeField(null=True, blank=True)
    washing_completed_at = models.DateTimeField(null=True, blank=True)
    drying_started_at = models.DateTimeField(null=True, blank=True)
    drying_completed_at = models.DateTimeField(null=True, blank=True)
    ironing_started_at = models.DateTimeField(null=True, blank=True)
    ironing_completed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Quality metrics
    quality_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )  # 1-10 scale
    quality_notes = models.TextField(blank=True)

    # Staff assignment
    processed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_items'
    )

    # Additional charges
    additional_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    additional_charges_reason = models.TextField(blank=True)

    # Notes
    processing_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_item_processing'
        verbose_name = 'Order Item Processing'
        verbose_name_plural = 'Order Item Processing'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order_item', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.order_item} - {self.get_status_display()}"

    @property
    def order(self):
        """Get the parent order."""
        return self.order_item.order

    def calculate_processing_time(self):
        """Calculate total processing time for this item."""
        if not self.completed_at or not self.inspection_at:
            return None
        duration = (self.completed_at - self.inspection_at).total_seconds() / 3600
        return round(duration, 2)  # Hours


class PartnerOrderNote(models.Model):
    """
    Internal notes that partners can add to orders.

    For communication between partner staff members
    about specific orders or items.
    """

    NOTE_TYPE = [
        ('general', 'General Note'),
        ('issue', 'Issue/Problem'),
        ('customer_request', 'Customer Request'),
        ('internal', 'Internal Communication'),
        ('quality', 'Quality Concern'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='partner_notes'
    )

    note_type = models.CharField(max_length=30, choices=NOTE_TYPE, default='general')
    content = models.TextField()

    # Attachments
    attachments = models.JSONField(default=list, blank=True)  # Photos/docs

    # Priority
    is_urgent = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    # Author
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='partner_order_notes'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'partner_order_notes'
        verbose_name = 'Partner Order Note'
        verbose_name_plural = 'Partner Order Notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', '-created_at']),
            models.Index(fields=['is_urgent', '-created_at']),
        ]

    def __str__(self):
        return f"Note for {self.order.order_number} by {self.created_by.email}"


class DeliveryProof(models.Model):
    """
    Delivery proof with photos and signature.

    Captures evidence of successful delivery including
    photos and customer signature.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery_proof'
    )

    # Photos
    package_photos = models.JSONField(default=list, blank=True)  # Photos of packages
    delivery_location_photo = models.CharField(max_length=500, blank=True)

    # Signature
    customer_signature = models.CharField(max_length=500, blank=True)  # Base64 or URL
    signature_name = models.CharField(max_length=255, blank=True)

    # Details
    delivered_to = models.CharField(max_length=255, blank=True)  # Name of recipient
    delivered_to_relation = models.CharField(max_length=100, blank=True)  # Self, Family, etc.

    # Location
    delivery_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    delivery_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Timing
    delivered_at = models.DateTimeField(default=timezone.now)

    # Notes
    delivery_notes = models.TextField(blank=True)

    # Delivered by
    delivered_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='deliveries_made'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_proofs'
        verbose_name = 'Delivery Proof'
        verbose_name_plural = 'Delivery Proofs'

    def __str__(self):
        return f"Delivery proof for {self.order.order_number}"

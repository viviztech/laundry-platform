"""
Management command to load default notification templates.
"""
from django.core.management.base import BaseCommand
from apps.notifications.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Load default notification templates into the database'

    def handle(self, *args, **options):
        """Load default templates."""
        templates = [
            # Order notifications
            {
                'type': 'order_created',
                'name': 'Order Created',
                'description': 'Sent when a new order is placed',
                'email_subject': 'Order Confirmation #{{ order.order_number }}',
                'title_template': 'Order Placed Successfully',
                'message_template': 'Your order #{{ order.order_number }} has been placed successfully. Total: ₹{{ order.total_amount }}',
                'sms_template': 'LaundryConnect: Order #{{ order.order_number }} placed successfully. Total: ₹{{ order.total_amount }}. Track at laundryconnect.com/orders',
                'action_url_template': '/orders/{{ order.id }}',
            },
            {
                'type': 'order_confirmed',
                'name': 'Order Confirmed',
                'description': 'Sent when order is confirmed by admin/system',
                'email_subject': 'Order Confirmed #{{ order.order_number }}',
                'title_template': 'Order Confirmed',
                'message_template': 'Your order #{{ order.order_number }} has been confirmed and will be picked up on {{ order.pickup_date }}',
                'sms_template': 'LaundryConnect: Order #{{ order.order_number }} confirmed! Pickup scheduled for {{ order.pickup_date }}. Thank you!',
                'action_url_template': '/orders/{{ order.id }}',
            },
            {
                'type': 'order_picked_up',
                'name': 'Order Picked Up',
                'description': 'Sent when order is picked up',
                'email_subject': 'Order Picked Up #{{ order.order_number }}',
                'title_template': 'Order Picked Up',
                'message_template': 'Your laundry has been picked up and is on its way to our facility.',
                'sms_template': 'LaundryConnect: Your laundry (Order #{{ order.order_number }}) has been picked up. Processing will begin shortly.',
                'action_url_template': '/orders/{{ order.id }}',
            },
            {
                'type': 'order_in_progress',
                'name': 'Order In Progress',
                'description': 'Sent when order processing starts',
                'email_subject': 'Order In Progress #{{ order.order_number }}',
                'title_template': 'Order Processing Started',
                'message_template': 'We are currently processing your laundry. It will be ready soon!',
                'sms_template': 'LaundryConnect: Your order #{{ order.order_number }} is now being processed. We\'ll notify you when it\'s ready!',
                'action_url_template': '/orders/{{ order.id }}',
            },
            {
                'type': 'order_ready',
                'name': 'Order Ready for Delivery',
                'description': 'Sent when order is ready for delivery',
                'email_subject': 'Order Ready for Delivery #{{ order.order_number }}',
                'title_template': 'Your Order is Ready!',
                'message_template': 'Your laundry is ready and will be delivered soon.',
                'sms_template': 'LaundryConnect: Good news! Your order #{{ order.order_number }} is ready and will be delivered soon.',
                'action_url_template': '/orders/{{ order.id }}',
            },
            {
                'type': 'order_out_for_delivery',
                'name': 'Order Out for Delivery',
                'description': 'Sent when order is out for delivery',
                'email_subject': 'Order Out for Delivery #{{ order.order_number }}',
                'title_template': 'Out for Delivery',
                'message_template': 'Your order is out for delivery and will reach you shortly.',
                'sms_template': 'LaundryConnect: Your order #{{ order.order_number }} is out for delivery! It will reach you shortly. Track live at laundryconnect.com',
                'action_url_template': '/orders/{{ order.id }}',
            },
            {
                'type': 'order_delivered',
                'name': 'Order Delivered',
                'description': 'Sent when order is delivered',
                'email_subject': 'Order Delivered #{{ order.order_number }}',
                'title_template': 'Order Delivered',
                'message_template': 'Your order has been delivered successfully. Thank you for choosing LaundryConnect!',
                'sms_template': 'LaundryConnect: Order #{{ order.order_number }} delivered successfully! Thank you for choosing us. Rate your experience at laundryconnect.com',
                'action_url_template': '/orders/{{ order.id }}/review',
            },
            {
                'type': 'order_cancelled',
                'name': 'Order Cancelled',
                'description': 'Sent when order is cancelled',
                'email_subject': 'Order Cancelled #{{ order.order_number }}',
                'title_template': 'Order Cancelled',
                'message_template': 'Your order #{{ order.order_number }} has been cancelled.',
                'sms_template': 'LaundryConnect: Order #{{ order.order_number }} has been cancelled. If you have any questions, contact support.',
                'action_url_template': '/orders',
            },

            # Payment notifications
            {
                'type': 'payment_initiated',
                'name': 'Payment Initiated',
                'description': 'Sent when payment process starts',
                'email_subject': 'Payment Initiated - LaundryConnect',
                'title_template': 'Payment Processing',
                'message_template': 'Your payment of ₹{{ payment.amount }} is being processed.',
                'sms_template': 'LaundryConnect: Payment of ₹{{ payment.amount }} is being processed. We\'ll notify you once complete.',
                'action_url_template': '/payments/{{ payment.id }}',
            },
            {
                'type': 'payment_completed',
                'name': 'Payment Completed',
                'description': 'Sent when payment is successful',
                'email_subject': 'Payment Successful - ₹{{ payment.amount }}',
                'title_template': 'Payment Successful',
                'message_template': 'Your payment of ₹{{ payment.amount }} has been completed successfully.',
                'sms_template': 'LaundryConnect: Payment of ₹{{ payment.amount }} successful! Transaction ID: {{ payment.transaction_id }}. Thank you!',
                'action_url_template': '/payments/{{ payment.id }}/receipt',
            },
            {
                'type': 'payment_failed',
                'name': 'Payment Failed',
                'description': 'Sent when payment fails',
                'email_subject': 'Payment Failed - LaundryConnect',
                'title_template': 'Payment Failed',
                'message_template': 'Your payment of ₹{{ payment.amount }} could not be processed. Please try again.',
                'sms_template': 'LaundryConnect: Payment of ₹{{ payment.amount }} failed. Please try again or contact support.',
                'action_url_template': '/payments/{{ payment.id }}/retry',
            },
            {
                'type': 'payment_refunded',
                'name': 'Payment Refunded',
                'description': 'Sent when payment is refunded',
                'email_subject': 'Payment Refunded - ₹{{ payment.amount }}',
                'title_template': 'Payment Refunded',
                'message_template': 'Your payment of ₹{{ payment.amount }} has been refunded to your account.',
                'sms_template': 'LaundryConnect: Refund of ₹{{ payment.amount }} has been processed to your account. Check in 5-7 business days.',
                'action_url_template': '/payments/{{ payment.id }}',
            },

            # Refund notifications
            {
                'type': 'refund_requested',
                'name': 'Refund Requested',
                'description': 'Sent when refund is requested',
                'email_subject': 'Refund Request Received - LaundryConnect',
                'title_template': 'Refund Request Received',
                'message_template': 'We have received your refund request. It will be processed within 5-7 business days.',
                'sms_template': 'LaundryConnect: Your refund request has been received. Processing will take 5-7 business days.',
                'action_url_template': '/refunds',
            },
            {
                'type': 'refund_processing',
                'name': 'Refund Processing',
                'description': 'Sent when refund is being processed',
                'email_subject': 'Refund Processing - LaundryConnect',
                'title_template': 'Refund Being Processed',
                'message_template': 'Your refund is currently being processed.',
                'sms_template': 'LaundryConnect: Your refund is now being processed. You\'ll receive it within 5-7 business days.',
                'action_url_template': '/refunds',
            },
            {
                'type': 'refund_completed',
                'name': 'Refund Completed',
                'description': 'Sent when refund is completed',
                'email_subject': 'Refund Completed - LaundryConnect',
                'title_template': 'Refund Completed',
                'message_template': 'Your refund has been processed successfully.',
                'sms_template': 'LaundryConnect: Your refund has been completed successfully. Amount will reflect in your account soon.',
                'action_url_template': '/refunds',
            },

            # Partner notifications
            {
                'type': 'partner_assigned',
                'name': 'Partner Assigned',
                'description': 'Sent when partner is assigned to order',
                'email_subject': 'Partner Assigned to Your Order',
                'title_template': 'Partner Assigned',
                'message_template': 'A partner has been assigned to handle your order.',
                'sms_template': 'LaundryConnect: A partner has been assigned to your order #{{ order.order_number }}. Track updates at laundryconnect.com',
                'action_url_template': '/orders/{{ order.id }}',
            },
            {
                'type': 'partner_approved',
                'name': 'Partner Account Approved',
                'description': 'Sent when partner account is approved',
                'email_subject': 'Your Partner Account is Approved!',
                'title_template': 'Account Approved',
                'message_template': 'Congratulations! Your partner account has been approved. You can now start accepting orders.',
                'sms_template': 'LaundryConnect: Congratulations! Your partner account is approved. Login to start accepting orders.',
                'action_url_template': '/partner/dashboard',
            },
            {
                'type': 'new_order_assigned',
                'name': 'New Order Assigned to Partner',
                'description': 'Sent to partner when new order is assigned',
                'email_subject': 'New Order Assigned #{{ order.order_number }}',
                'title_template': 'New Order Assigned',
                'message_template': 'A new order #{{ order.order_number }} has been assigned to you.',
                'sms_template': 'LaundryConnect: New order #{{ order.order_number }} assigned! Amount: ₹{{ order.total_amount }}. Check app for details.',
                'action_url_template': '/partner/orders/{{ order.id }}',
            },

            # Account notifications
            {
                'type': 'welcome',
                'name': 'Welcome to LaundryConnect',
                'description': 'Sent when user registers',
                'email_subject': 'Welcome to LaundryConnect!',
                'title_template': 'Welcome to LaundryConnect',
                'message_template': 'Thank you for joining LaundryConnect. We\'re excited to serve you!',
                'sms_template': 'Welcome to LaundryConnect! Get 20% OFF on your first order. Use code: WELCOME20. Download our app now!',
                'action_url_template': '/profile',
            },
            {
                'type': 'account_verified',
                'name': 'Account Verified',
                'description': 'Sent when account is verified',
                'email_subject': 'Account Verified - LaundryConnect',
                'title_template': 'Account Verified',
                'message_template': 'Your account has been successfully verified.',
                'sms_template': 'LaundryConnect: Your account has been verified successfully. You can now place orders!',
                'action_url_template': '/profile',
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = NotificationTemplate.objects.update_or_create(
                type=template_data['type'],
                defaults={
                    'name': template_data['name'],
                    'description': template_data['description'],
                    'email_subject': template_data['email_subject'],
                    'email_body_html': f'<p>{template_data["message_template"]}</p>',
                    'email_body_text': template_data['message_template'],
                    'title_template': template_data['title_template'],
                    'message_template': template_data['message_template'],
                    'sms_template': template_data.get('sms_template', ''),
                    'action_url_template': template_data.get('action_url_template', ''),
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully loaded {created_count} new templates '
                f'and updated {updated_count} existing templates.'
            )
        )

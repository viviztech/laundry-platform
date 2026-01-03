"""
Management command to test SMS notification functionality.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notifications.sms import sms_service

User = get_user_model()


class Command(BaseCommand):
    help = 'Test SMS notification sending'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number to send test SMS (E.164 format: +919876543210)',
        )
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email of user to send test notification SMS',
        )
        parser.add_argument(
            '--message',
            type=str,
            default='This is a test message from LaundryConnect!',
            help='Custom test message',
        )
        parser.add_argument(
            '--check-config',
            action='store_true',
            help='Check if SMS service is configured correctly',
        )

    def handle(self, *args, **options):
        """Test SMS functionality."""

        # Check configuration
        if options['check_config']:
            self.check_sms_configuration()
            return

        # Send test SMS to phone number
        if options['phone']:
            self.send_test_sms_to_phone(
                options['phone'],
                options['message']
            )
            return

        # Send test notification SMS to user
        if options['user_email']:
            self.send_test_notification_to_user(options['user_email'])
            return

        # No arguments provided, show help
        self.stdout.write(
            self.style.WARNING(
                'No action specified. Use --help to see available options.'
            )
        )
        self.check_sms_configuration()

    def check_sms_configuration(self):
        """Check if SMS service is configured."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('SMS Configuration Check'))
        self.stdout.write('='*60)

        if sms_service.is_enabled():
            self.stdout.write(
                self.style.SUCCESS('✓ SMS service is enabled and configured')
            )
            self.stdout.write(f'  Account SID: {sms_service.account_sid[:10]}...')
            self.stdout.write(f'  From Number: {sms_service.from_number}')
        else:
            self.stdout.write(
                self.style.ERROR('✗ SMS service is NOT configured')
            )
            self.stdout.write('\nTo configure SMS:')
            self.stdout.write('1. Sign up at https://www.twilio.com/')
            self.stdout.write('2. Get your Account SID, Auth Token, and Phone Number')
            self.stdout.write('3. Add to your .env file:')
            self.stdout.write('   TWILIO_ACCOUNT_SID=your_account_sid')
            self.stdout.write('   TWILIO_AUTH_TOKEN=your_auth_token')
            self.stdout.write('   TWILIO_PHONE_NUMBER=+1234567890')

        self.stdout.write('='*60 + '\n')

    def send_test_sms_to_phone(self, phone_number, message):
        """Send test SMS to a phone number."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('Sending Test SMS'))
        self.stdout.write('='*60)

        if not sms_service.is_enabled():
            self.stdout.write(
                self.style.ERROR('SMS service is not configured. Cannot send SMS.')
            )
            self.check_sms_configuration()
            return

        self.stdout.write(f'To: {phone_number}')
        self.stdout.write(f'Message: {message}')
        self.stdout.write('')

        # Send SMS
        result = sms_service.send_sms(
            to_number=phone_number,
            message=message,
            notification_id='TEST'
        )

        # Display result
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✓ SMS sent successfully!')
            )
            self.stdout.write(f'  Message SID: {result["message_sid"]}')
            self.stdout.write(f'  Status: {result["status"]}')
            if result.get('price'):
                self.stdout.write(f'  Cost: {result["price"]} {result["price_unit"]}')
        else:
            self.stdout.write(
                self.style.ERROR('✗ SMS sending failed')
            )
            self.stdout.write(f'  Error: {result.get("error")}')

        self.stdout.write('='*60 + '\n')

    def send_test_notification_to_user(self, user_email):
        """Send test notification SMS to a user."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('Sending Test Notification SMS'))
        self.stdout.write('='*60)

        if not sms_service.is_enabled():
            self.stdout.write(
                self.style.ERROR('SMS service is not configured. Cannot send SMS.')
            )
            self.check_sms_configuration()
            return

        # Get user
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {user_email} not found')
            )
            return

        # Check user has phone
        if not user.phone:
            self.stdout.write(
                self.style.ERROR(f'User {user_email} has no phone number')
            )
            return

        self.stdout.write(f'User: {user.email}')
        self.stdout.write(f'Phone: {user.phone}')
        self.stdout.write(f'Notification Type: welcome')
        self.stdout.write('')

        # Send notification SMS
        context = {
            'user': user,
            'first_name': user.first_name or 'Valued Customer',
        }

        result = sms_service.send_notification_sms(
            user=user,
            notification_type='welcome',
            context=context
        )

        # Display result
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✓ Notification SMS sent successfully!')
            )
            self.stdout.write(f'  Message SID: {result["message_sid"]}')
            self.stdout.write(f'  Status: {result["status"]}')
            if result.get('price'):
                self.stdout.write(f'  Cost: {result["price"]} {result["price_unit"]}')
        else:
            self.stdout.write(
                self.style.ERROR('✗ Notification SMS sending failed')
            )
            self.stdout.write(f'  Error: {result.get("error")}')

        self.stdout.write('='*60 + '\n')


    def verify_phone_number(self, phone_number):
        """Verify a phone number using Twilio Lookup API."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('Verifying Phone Number'))
        self.stdout.write('='*60)

        if not sms_service.is_enabled():
            self.stdout.write(
                self.style.ERROR('SMS service is not configured.')
            )
            return

        self.stdout.write(f'Phone: {phone_number}')
        self.stdout.write('')

        is_valid = sms_service.verify_phone_number(phone_number)

        if is_valid:
            self.stdout.write(
                self.style.SUCCESS('✓ Phone number is valid')
            )
        else:
            self.stdout.write(
                self.style.ERROR('✗ Phone number is invalid or cannot be verified')
            )

        self.stdout.write('='*60 + '\n')

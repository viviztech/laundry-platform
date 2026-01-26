"""
Management command to generate VAPID keys for Web Push notifications.
"""
from django.core.management.base import BaseCommand
from py_vapid import Vapid


class Command(BaseCommand):
    help = 'Generate VAPID keys for Web Push notifications'

    def handle(self, *args, **options):
        """Generate new VAPID key pair."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('Generating VAPID Keys for Web Push'))
        self.stdout.write('='*60)

        # Generate VAPID keys
        vapid = Vapid()
        vapid.generate_keys()

        # Get private and public keys
        private_key = vapid.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        public_key = vapid.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )

        # Convert public key to base64url format
        import base64
        public_key_b64 = base64.urlsafe_b64encode(public_key).decode('utf-8').rstrip('=')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ VAPID keys generated successfully!'))
        self.stdout.write('')
        self.stdout.write('Add these to your .env file:')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('VAPID_PRIVATE_KEY="{}..."'.format(private_key[:50])))
        self.stdout.write(self.style.WARNING('VAPID_PUBLIC_KEY="{}"'.format(public_key_b64)))
        self.stdout.write(self.style.WARNING('VAPID_ADMIN_EMAIL="mailto:admin@laundryconnect.com"'))
        self.stdout.write('')
        self.stdout.write('Full keys (copy these to .env):')
        self.stdout.write('')
        self.stdout.write(f'VAPID_PRIVATE_KEY="{private_key.strip()}"')
        self.stdout.write(f'VAPID_PUBLIC_KEY="{public_key_b64}"')
        self.stdout.write('VAPID_ADMIN_EMAIL="mailto:admin@laundryconnect.com"')
        self.stdout.write('')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('✓ Done! Copy the keys above to your .env file'))
        self.stdout.write('='*60 + '\n')


# Import required for PEM encoding
from cryptography.hazmat.primitives import serialization

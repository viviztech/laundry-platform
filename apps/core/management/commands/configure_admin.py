"""
Management command to configure admin panel visibility
Usage: python manage.py configure_admin
"""
from django.core.management.base import BaseCommand
from django.contrib import admin
from config.admin_config import OPTIONAL_MODULES

class Command(BaseCommand):
    help = 'Configure admin panel by hiding optional modules'

    def handle(self, *args, **options):
        self.stdout.write('Configuring admin panel for partner launch...')

        hidden_count = 0

        # Unregister optional models
        for app_label, models in OPTIONAL_MODULES.items():
            for model_name in models:
                try:
                    # Get the model class
                    from django.apps import apps
                    model_class = apps.get_model(app_label, model_name)

                    # Check if it's registered
                    if model_class in admin.site._registry:
                        admin.site.unregister(model_class)
                        hidden_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ Hidden: {app_label}.{model_name}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Could not hide {app_label}.{model_name}: {e}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Admin panel configured! Hidden {hidden_count} optional modules.')
        )
        self.stdout.write('To enable hidden modules, update feature flags in config/admin_config.py')

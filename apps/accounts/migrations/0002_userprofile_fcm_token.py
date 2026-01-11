# Generated manually for push notification support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='fcm_token',
            field=models.TextField(blank=True, help_text='Firebase Cloud Messaging token for push notifications'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='fcm_platform',
            field=models.CharField(blank=True, choices=[('ios', 'iOS'), ('android', 'Android')], max_length=10),
        ),
    ]

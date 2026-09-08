import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stage', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='pesapal_tracking_id',
            field=models.CharField(blank=True, help_text="Pesapal's OrderTrackingId for this payment, if paid via Pesapal.", max_length=100),
        ),
        migrations.AddField(
            model_name='ticket',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='stage/tickets/qrcodes/'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='checked_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ticket',
            name='checked_in_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='checked_in_by',
            field=models.ForeignKey(blank=True, help_text='Which staff member scanned/checked this ticket in at the door.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets_checked_in', to=settings.AUTH_USER_MODEL),
        ),
    ]

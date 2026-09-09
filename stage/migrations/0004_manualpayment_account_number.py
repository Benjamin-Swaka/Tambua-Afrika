from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stage', '0003_manualpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='manualpayment',
            name='account_number',
            field=models.CharField(
                default='8126862',
                help_text='M-Pesa Paybill account number supplied to the customer.',
                max_length=30,
            ),
        ),
    ]

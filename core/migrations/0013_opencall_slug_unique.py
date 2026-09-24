from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_backfill_open_call_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opencall',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=220,
                unique=True,
                help_text="Used in the open call's own URL. Auto-generated from the title if left blank.",
            ),
        ),
    ]

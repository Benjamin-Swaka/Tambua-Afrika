from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_consentlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedWork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('department_label', models.CharField(help_text="Shown as the small eyebrow label, e.g. 'Tambua Ink'.", max_length=100)),
                ('category', models.CharField(choices=[('book', 'Book'), ('comic', 'Comic'), ('play', 'Play'), ('animation', 'Animation')], default='book', max_length=20)),
                ('author_meta', models.CharField(blank=True, help_text="e.g. 'by A. K. Mwangi · 2025'", max_length=150)),
                ('link_url', models.CharField(blank=True, help_text="Where the 'Read More' / 'Explore' button goes. Leave blank for '#'.", max_length=300)),
                ('link_text', models.CharField(default='Read More', max_length=40)),
                ('background_color', models.CharField(default='#e8e0d8', max_length=7)),
                ('icon_emoji', models.CharField(default='📖', max_length=8)),
                ('image', models.ImageField(blank=True, null=True, upload_to='home/featured_works/')),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OpenCall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('open', 'Open'), ('closing_soon', 'Closing Soon'), ('closed', 'Closed')], default='open', max_length=20)),
                ('deadline_label', models.CharField(help_text="e.g. 'Closes 31 Dec 2026' — free text so past calls can say 'Closed 30 Jun 2026'.", max_length=100)),
                ('categories_label', models.CharField(help_text="e.g. 'Manuscripts · Poetry · Short Stories · Scripts'", max_length=200)),
                ('link_url', models.CharField(blank=True, help_text='Leave blank to use the Submissions page.', max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ShopHighlight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=250)),
                ('price_label', models.CharField(help_text="e.g. 'From $14.99'", max_length=60)),
                ('link_url', models.CharField(blank=True, help_text='Leave blank to use the Shop homepage.', max_length=300)),
                ('link_text', models.CharField(default='Browse', max_length=40)),
                ('background_color', models.CharField(default='#e8e0d8', max_length=7)),
                ('icon_emoji', models.CharField(default='🛍️', max_length=8)),
                ('image', models.ImageField(blank=True, null=True, upload_to='home/shop_highlights/')),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['order', '-created_at'],
            },
        ),
    ]

from django.db import migrations, models


def backfill_open_call_slugs(apps, schema_editor):
    from django.utils.text import slugify

    OpenCall = apps.get_model('core', 'OpenCall')
    seen = set(
        OpenCall.objects.exclude(slug='').values_list('slug', flat=True)
    )
    for call in OpenCall.objects.filter(slug=''):
        base_slug = slugify(call.title) or 'open-call'
        slug = base_slug
        counter = 2
        while slug in seen:
            slug = f"{base_slug}-{counter}"
            counter += 1
        seen.add(slug)
        call.slug = slug
        call.save(update_fields=['slug'])


def noop_reverse(apps, schema_editor):
    # Nothing to undo -- reversing just leaves the slugs in place, which is
    # harmless since the (now-removed) slug field wouldn't be read anyway.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_homedepartment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opencall',
            name='description',
            field=models.TextField(help_text='Short summary shown on the open call card.'),
        ),
        migrations.AlterField(
            model_name='opencall',
            name='link_url',
            field=models.CharField(
                blank=True,
                max_length=300,
                help_text=(
                    "Optional external URL (e.g. guidelines hosted elsewhere). When set, "
                    "'View Guidelines' sends people straight there instead of to this "
                    "call's own details page. Leave blank to use the details page."
                ),
            ),
        ),
        migrations.AddField(
            model_name='opencall',
            name='guidelines',
            field=models.TextField(
                blank=True,
                default='',
                help_text=(
                    "Full submission guidelines shown on this call's own dedicated page "
                    "(eligibility, format, judging criteria, etc). Leave blank to just "
                    "show the short summary above on that page too."
                ),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opencall',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=220),
        ),
        migrations.RunPython(backfill_open_call_slugs, noop_reverse),
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
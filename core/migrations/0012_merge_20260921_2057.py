from django.db import migrations
from django.utils.text import slugify


def backfill_open_call_slugs(apps, schema_editor):
    OpenCall = apps.get_model('core', 'OpenCall')
    seen = set(
        OpenCall.objects.exclude(slug='').values_list('slug', flat=True)
    )
    for call in OpenCall.objects.filter(slug='').order_by('pk'):
        base_slug = slugify(call.title)[:200] or 'open-call'
        slug = base_slug
        counter = 2
        while slug in seen:
            slug = f"{base_slug}-{counter}"
            counter += 1
        seen.add(slug)
        call.slug = slug
        call.save(update_fields=['slug'])


def noop_reverse(apps, schema_editor):
    # Reversing leaves slugs in place; harmless once the field is removed.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_opencall_guidelines_opencall_slug_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_open_call_slugs, noop_reverse),
    ]
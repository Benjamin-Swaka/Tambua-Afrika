from django.db import migrations


DEPARTMENTS = [
    {
        'name': 'Tambua Ink',
        'slug': 'ink',
        'color': '#003366',
        'description': 'Publishing — books, novellas, and written African stories.',
    },
    {
        'name': 'Tambua Stage',
        'slug': 'stage',
        'color': '#5D4037',
        'description': 'Theatre — live performance and voice acting.',
    },
    {
        'name': 'Tambua Comics',
        'slug': 'comics',
        'color': '#6c757d',
        'description': 'Visual storytelling — comics and graphic art.',
    },
    {
        'name': 'Tambua Shop',
        'slug': 'shop',
        'color': '#D2B48C',
        'description': 'Merchandise and products from the studio.',
    },
]


def seed_departments(apps, schema_editor):
    Department = apps.get_model('core', 'Department')
    for dept in DEPARTMENTS:
        Department.objects.get_or_create(slug=dept['slug'], defaults=dept)


def remove_departments(apps, schema_editor):
    Department = apps.get_model('core', 'Department')
    Department.objects.filter(slug__in=[d['slug'] for d in DEPARTMENTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_department_emailotp_userprofile_departmentmembership'),
    ]

    operations = [
        migrations.RunPython(seed_departments, remove_departments),
    ]

from django.db import migrations


FEATURED_WORKS = [
    {
        'title': 'Echoes of the Savanna', 'department_label': 'Tambua Ink', 'category': 'book',
        'author_meta': 'by A. K. Mwangi · 2025', 'link_text': 'Read More',
        'background_color': '#e8e0d8', 'icon_emoji': '📖', 'order': 1,
    },
    {
        'title': 'The Golden Mask', 'department_label': 'Tambua Comics', 'category': 'comic',
        'author_meta': 'by S. O. Adebayo · 2025', 'link_text': 'Explore',
        'background_color': '#d0d0d0', 'icon_emoji': '🎨', 'order': 2,
    },
    {
        'title': 'The Griot\u2019s Daughter', 'department_label': 'Tambua Stage', 'category': 'play',
        'author_meta': 'by L. N. Okafor · 2025', 'link_text': 'View',
        'background_color': '#d4c4b0', 'icon_emoji': '🎭', 'order': 3,
    },
    {
        'title': 'Spirit of the Baobab', 'department_label': 'Tambua Comics', 'category': 'animation',
        'author_meta': 'by K. D. Mensah · 2025', 'link_text': 'Watch',
        'background_color': '#c0d4e8', 'icon_emoji': '🎬', 'order': 4,
    },
]

OPEN_CALLS = [
    {
        'title': '2026 Annual Anthology', 'status': 'open',
        'description': 'Manuscripts, poetry collections, and short stories from African writers worldwide.',
        'deadline_label': 'Closes 31 Dec 2026',
        'categories_label': 'Manuscripts · Poetry · Short Stories · Scripts',
        'order': 1,
    },
    {
        'title': 'Stage Play Competition', 'status': 'closing_soon',
        'description': 'Original one-act plays by African playwrights. Selected works will be produced in 2027.',
        'deadline_label': 'Closes 15 Oct 2026',
        'categories_label': 'Plays · Scripts',
        'order': 2,
    },
    {
        'title': 'Graphic Novel Fellowship', 'status': 'closed',
        'description': 'Emerging African comic artists. The next fellowship round opens early 2027.',
        'deadline_label': 'Closed 30 Jun 2026',
        'categories_label': 'Comics · Illustration',
        'order': 3,
    },
]

SHOP_HIGHLIGHTS = [
    {
        'title': 'Best-Selling Books', 'description': 'Novels, poetry, and literary journals',
        'price_label': 'From $14.99', 'link_text': 'Browse',
        'background_color': '#e8e0d8', 'icon_emoji': '📚', 'order': 1,
    },
    {
        'title': 'Merchandise', 'description': 'Apparel, accessories, and collectibles',
        'price_label': 'From $24.99', 'link_text': 'Shop Now',
        'background_color': '#d4c9b0', 'icon_emoji': '👕', 'order': 2,
    },
    {
        'title': 'Tickets', 'description': 'Live performances, readings, and events',
        'price_label': 'From $12.00', 'link_text': 'Get Tickets',
        'background_color': '#d4c4b0', 'icon_emoji': '🎫', 'order': 3,
    },
]


def seed(apps, schema_editor):
    FeaturedWork = apps.get_model('core', 'FeaturedWork')
    OpenCall = apps.get_model('core', 'OpenCall')
    ShopHighlight = apps.get_model('core', 'ShopHighlight')

    for row in FEATURED_WORKS:
        FeaturedWork.objects.create(**row)
    for row in OPEN_CALLS:
        OpenCall.objects.create(**row)
    for row in SHOP_HIGHLIGHTS:
        ShopHighlight.objects.create(**row)


def unseed(apps, schema_editor):
    apps.get_model('core', 'FeaturedWork').objects.all().delete()
    apps.get_model('core', 'OpenCall').objects.all().delete()
    apps.get_model('core', 'ShopHighlight').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_homepage_content'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]

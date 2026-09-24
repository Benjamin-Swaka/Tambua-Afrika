from django.db import migrations, models


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
        # db_index=False is the key fix: the unique AlterField in 0013 creates
        # the index (and its Postgres "_like" twin) itself. Letting AddField
        # queue the same index caused DuplicateTable.
        migrations.AddField(
            model_name='opencall',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=220, db_index=False),
        ),
    ]
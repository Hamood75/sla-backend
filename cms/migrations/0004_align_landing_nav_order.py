from django.db import migrations

NAV_ITEMS = [
    ('Home', '#home', 1),
    ('Gallery', '#gallery', 2),
    ('About', '#about', 3),
    ('Values', '#values', 4),
    ('Programs', '#services', 5),
    ('Team', '#team', 6),
    ('Contact', '#contact', 7),
]


def align_nav_order(apps, schema_editor):
    NavItem = apps.get_model('cms', 'NavItem')
    for label, href, order in NAV_ITEMS:
        NavItem.objects.update_or_create(
            href=href,
            defaults={'label': label, 'order': order, 'is_active': True},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('cms', '0003_contact_message_reply'),
    ]

    operations = [
        migrations.RunPython(align_nav_order, migrations.RunPython.noop),
    ]

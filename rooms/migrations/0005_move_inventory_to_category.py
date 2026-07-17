from django.db import migrations, models


def copy_inventory_to_categories(apps, schema_editor):
    Room = apps.get_model('rooms', 'Room')
    RoomCategory = apps.get_model('rooms', 'RoomCategory')

    for category in RoomCategory.objects.all():
        max_rooms = Room.objects.filter(category=category).aggregate(
            max_total=models.Max('total_rooms')
        )['max_total'] or 1
        category.total_rooms = max_rooms
        category.save(update_fields=['total_rooms'])


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_add_rooms_booked_to_room_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomcategory',
            name='total_rooms',
            field=models.PositiveIntegerField(default=1, help_text='Total physical rooms available for this category across all currencies'),
        ),
        migrations.RunPython(copy_inventory_to_categories, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='room',
            name='category',
            field=models.ForeignKey(help_text='Room category (managed in admin under Room Categories)', on_delete=models.PROTECT, related_name='rooms', to='rooms.roomcategory'),
        ),
        migrations.AlterField(
            model_name='room',
            name='tax_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, help_text='Optional tax percentage for this room listing', max_digits=5, null=True),
        ),
        migrations.RemoveField(
            model_name='room',
            name='total_rooms',
        ),
    ]

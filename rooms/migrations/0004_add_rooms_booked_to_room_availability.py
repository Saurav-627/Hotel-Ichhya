from django.db import migrations, models


def consolidate_occupancies(apps, schema_editor):
    RoomAvailability = apps.get_model('rooms', 'RoomAvailability')

    duplicates = (
        RoomAvailability.objects
        .filter(booking__isnull=False)
        .values('room_id', 'date', 'booking_id')
        .annotate(row_count=models.Count('id'))
        .filter(row_count__gt=1)
    )

    for row in duplicates:
        rows = list(
            RoomAvailability.objects.filter(
                room_id=row['room_id'],
                date=row['date'],
                booking_id=row['booking_id'],
            ).order_by('id')
        )
        keeper = rows[0]
        keeper.rooms_booked = len(rows)
        keeper.save(update_fields=['rooms_booked'])
        for duplicate in rows[1:]:
            duplicate.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_remove_unique_together_room_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomavailability',
            name='rooms_booked',
            field=models.PositiveIntegerField(default=1, help_text='Number of physical rooms occupied for this booking-night'),
        ),
        migrations.RunPython(consolidate_occupancies, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='roomavailability',
            constraint=models.UniqueConstraint(fields=('room', 'date', 'booking'), name='unique_room_booking_day_occupancy'),
        ),
    ]

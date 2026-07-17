from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_add_num_rooms_to_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending Payment'), ('confirmed', 'Confirmed'), ('checked_in', 'Checked In'), ('checked_out', 'Checked Out'), ('cancelled', 'Cancelled')], default='draft', max_length=20),
        ),
    ]

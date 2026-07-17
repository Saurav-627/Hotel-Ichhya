from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_add_draft_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='tax_amount',
            field=models.DecimalField(default=0.0, max_digits=10, decimal_places=2),
        ),
    ]

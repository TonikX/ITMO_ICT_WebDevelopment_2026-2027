                                               

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0002_reservation_end_date_reservation_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]

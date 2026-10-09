                                               

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]

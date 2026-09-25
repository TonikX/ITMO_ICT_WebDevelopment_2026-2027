from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_first_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='owners',
            field=models.ManyToManyField(related_name='cars', through='project_first_app.Ownership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='driverlicense',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ownership',
            name='car',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownerships', to='project_first_app.car'),
        ),
        migrations.AlterField(
            model_name='ownership',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownerships', to=settings.AUTH_USER_MODEL),
        ),
    ]

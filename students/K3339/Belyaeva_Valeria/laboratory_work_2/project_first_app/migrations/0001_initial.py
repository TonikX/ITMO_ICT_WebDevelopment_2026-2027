import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_number', models.CharField(max_length=15, unique=True, verbose_name='Государственный номер')),
                ('brand', models.CharField(max_length=20, verbose_name='Марка')),
                ('model', models.CharField(max_length=20, verbose_name='Модель')),
                ('color', models.CharField(blank=True, max_length=30, verbose_name='Цвет')),
            ],
            options={
                'verbose_name': 'автомобиль',
                'verbose_name_plural': 'автомобили',
                'ordering': ['registration_number'],
            },
        ),
        migrations.CreateModel(
            name='DriverLicense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10, verbose_name='Номер удостоверения')),
                ('category', models.CharField(max_length=10, verbose_name='Категория')),
                ('issued_at', models.DateField(verbose_name='Дата выдачи')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'водительское удостоверение',
                'verbose_name_plural': 'водительские удостоверения',
            },
        ),
        migrations.CreateModel(
            name='Ownership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project_first_app.car', verbose_name='Автомобиль')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'владение',
                'verbose_name_plural': 'владения',
            },
        ),
        migrations.AddField(
            model_name='car',
            name='owners',
            field=models.ManyToManyField(related_name='cars', through='project_first_app.Ownership', to=settings.AUTH_USER_MODEL, verbose_name='Владельцы'),
        ),
    ]

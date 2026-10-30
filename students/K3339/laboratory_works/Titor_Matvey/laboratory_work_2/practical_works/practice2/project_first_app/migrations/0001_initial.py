
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(max_length=30, verbose_name='Марка')),
                ('model', models.CharField(max_length=30, verbose_name='Модель')),
                ('color', models.CharField(max_length=30, verbose_name='Цвет')),
                ('state_number', models.CharField(max_length=10, verbose_name='Гос. номер')),
            ],
            options={
                'verbose_name': 'автомобиль',
                'verbose_name_plural': 'автомобили',
            },
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=30, verbose_name='Фамилия')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
            ],
            options={
                'verbose_name': 'владелец',
                'verbose_name_plural': 'владельцы',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Ownership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Дата покупки')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата продажи')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownerships', to='project_first_app.car')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownerships', to='project_first_app.owner')),
            ],
            options={
                'verbose_name': 'владение',
                'verbose_name_plural': 'владения',
            },
        ),
        migrations.AddField(
            model_name='car',
            name='owners',
            field=models.ManyToManyField(related_name='cars', through='project_first_app.Ownership', to='project_first_app.Owner'),
        ),
    ]

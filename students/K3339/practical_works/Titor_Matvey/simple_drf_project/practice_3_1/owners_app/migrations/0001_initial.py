
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
                ('brand', models.CharField(max_length=50, verbose_name='Марка')),
                ('model', models.CharField(max_length=50, verbose_name='Модель')),
                ('color', models.CharField(max_length=30, verbose_name='Цвет')),
                ('state_number', models.CharField(max_length=15, unique=True, verbose_name='Госномер')),
            ],
            options={
                'ordering': ['brand', 'model'],
            },
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('birth_date', models.DateField(verbose_name='Дата рождения')),
                ('passport', models.CharField(max_length=30, unique=True, verbose_name='Паспорт')),
                ('address', models.CharField(blank=True, max_length=200, verbose_name='Адрес')),
                ('nationality', models.CharField(blank=True, max_length=50, verbose_name='Национальность')),
            ],
            options={
                'ordering': ['last_name'],
            },
        ),
        migrations.CreateModel(
            name='Possession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateField(verbose_name='Дата начала владения')),
                ('ended_at', models.DateField(blank=True, null=True, verbose_name='Дата окончания владения')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='possessions', to='owners_app.car', verbose_name='Автомобиль')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='possessions', to='owners_app.owner', verbose_name='Владелец')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=30, unique=True, verbose_name='Номер удостоверения')),
                ('license_type', models.CharField(default='B', max_length=10, verbose_name='Тип')),
                ('issued_at', models.DateField(verbose_name='Дата выдачи')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='license', to='owners_app.owner', verbose_name='Владелец')),
            ],
            options={
                'ordering': ['-issued_at'],
            },
        ),
        migrations.AddField(
            model_name='car',
            name='owners',
            field=models.ManyToManyField(related_name='cars', through='owners_app.Possession', to='owners_app.owner', verbose_name='Владельцы'),
        ),
        migrations.AddConstraint(
            model_name='possession',
            constraint=models.UniqueConstraint(fields=('owner', 'car', 'started_at'), name='unique_possession_start'),
        ),
    ]

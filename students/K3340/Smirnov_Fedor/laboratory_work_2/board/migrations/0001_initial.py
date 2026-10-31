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
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10, verbose_name='Номер рейса')),
                ('airline', models.CharField(max_length=100, verbose_name='Авиакомпания')),
                ('kind', models.CharField(choices=[('departure', 'Вылет'), ('arrival', 'Прилёт')], max_length=10, verbose_name='Тип')),
                ('from_city', models.CharField(max_length=100, verbose_name='Откуда')),
                ('to_city', models.CharField(max_length=100, verbose_name='Куда')),
                ('takeoff', models.DateTimeField(verbose_name='Вылет')),
                ('landing', models.DateTimeField(verbose_name='Прилёт')),
                ('gate', models.CharField(max_length=5, verbose_name='Гейт')),
                ('seats', models.PositiveIntegerField(verbose_name='Мест в самолёте')),
            ],
            options={
                'verbose_name': 'рейс',
                'verbose_name_plural': 'рейсы',
                'ordering': ['takeoff'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_date', models.DateField(verbose_name='Дата рейса')),
                ('text', models.TextField(verbose_name='Комментарий')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], verbose_name='Оценка')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='board.flight', verbose_name='Рейс')),
            ],
            options={
                'verbose_name': 'отзыв',
                'verbose_name_plural': 'отзывы',
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat', models.PositiveIntegerField(verbose_name='Место')),
                ('ticket', models.CharField(blank=True, max_length=20, verbose_name='Номер билета')),
                ('checked_in', models.BooleanField(default=False, verbose_name='Зарегистрирован')),
                ('passenger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пассажир')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='board.flight', verbose_name='Рейс')),
            ],
            options={
                'verbose_name': 'бронь',
                'verbose_name_plural': 'брони',
                'unique_together': {('flight', 'seat')},
            },
        ),
    ]

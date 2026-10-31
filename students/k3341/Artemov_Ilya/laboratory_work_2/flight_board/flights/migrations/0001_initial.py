import django.core.validators
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
                ('number', models.CharField(max_length=12, verbose_name='Номер рейса')),
                ('airline', models.CharField(max_length=100, verbose_name='Авиакомпания')),
                ('origin', models.CharField(max_length=100, verbose_name='Аэропорт отправления')),
                ('destination', models.CharField(max_length=100, verbose_name='Аэропорт прибытия')),
                ('departure_at', models.DateTimeField(verbose_name='Время отлёта')),
                ('arrival_at', models.DateTimeField(verbose_name='Время прилёта')),
                ('direction', models.CharField(choices=[('arrival', 'Прилёт'), ('departure', 'Отлёт')], max_length=9, verbose_name='Тип')),
                ('gate', models.CharField(max_length=10, verbose_name='Номер гейта')),
                ('seat_count', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество мест')),
            ],
            options={
                'verbose_name': 'рейс',
                'verbose_name_plural': 'рейсы',
                'ordering': ['departure_at', 'pk'],
                'constraints': [models.UniqueConstraint(fields=('number', 'departure_at'), name='unique_flight_departure'), models.CheckConstraint(condition=models.Q(('arrival_at__gt', models.F('departure_at'))), name='flight_times_order'), models.CheckConstraint(condition=models.Q(('seat_count__gte', 1)), name='flight_positive_seats'), models.CheckConstraint(condition=models.Q(('direction__in', ['arrival', 'departure'])), name='flight_direction_valid')],
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passenger_name', models.CharField(max_length=150, verbose_name='ФИО пассажира')),
                ('seat_number', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Номер места')),
                ('ticket_number', models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='Номер билета')),
                ('checked_in', models.BooleanField(default=False, verbose_name='Зарегистрирован на рейс')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='flights.flight', verbose_name='Рейс')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'бронирование',
                'verbose_name_plural': 'бронирования',
                'ordering': ['flight_id', 'seat_number'],
                'constraints': [models.UniqueConstraint(fields=('flight', 'seat_number'), name='unique_flight_seat'), models.CheckConstraint(condition=models.Q(('seat_number__gte', 1)), name='reservation_positive_seat'), models.CheckConstraint(condition=models.Q(('checked_in', False), models.Q(('ticket_number__isnull', False), models.Q(('ticket_number', ''), _negated=True)), _connector='OR'), name='checkin_requires_ticket')],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_date', models.DateField(verbose_name='Дата рейса')),
                ('text', models.TextField(verbose_name='Текст отзыва')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Рейтинг')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='flights.flight', verbose_name='Рейс')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flight_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Комментатор')),
            ],
            options={
                'verbose_name': 'отзыв',
                'verbose_name_plural': 'отзывы',
                'ordering': ['-created_at', '-pk'],
                'constraints': [models.CheckConstraint(condition=models.Q(('rating__gte', 1), ('rating__lte', 10)), name='review_rating_1_10')],
            },
        ),
    ]

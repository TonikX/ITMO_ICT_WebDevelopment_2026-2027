import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('passport_number', models.CharField(blank=True, max_length=20, verbose_name='Номер паспорта')),
                ('home_address', models.CharField(blank=True, max_length=255, verbose_name='Домашний адрес')),
                ('nationality', models.CharField(blank=True, max_length=80, verbose_name='Национальность')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=12, verbose_name='Номер рейса')),
                ('airline', models.CharField(max_length=100, verbose_name='Авиакомпания')),
                ('origin', models.CharField(max_length=100, verbose_name='Город отправления')),
                ('origin_code', models.CharField(max_length=3, verbose_name='Код аэропорта отправления')),
                ('destination', models.CharField(max_length=100, verbose_name='Город прибытия')),
                ('destination_code', models.CharField(max_length=3, verbose_name='Код аэропорта прибытия')),
                ('departure_at', models.DateTimeField(verbose_name='Вылет')),
                ('arrival_at', models.DateTimeField(verbose_name='Прилёт')),
                ('kind', models.CharField(choices=[('departure', 'Вылет'), ('arrival', 'Прилёт')], default='departure', max_length=10, verbose_name='Тип')),
                ('gate', models.CharField(max_length=8, verbose_name='Гейт')),
                ('status', models.CharField(choices=[('scheduled', 'По расписанию'), ('boarding', 'Посадка'), ('delayed', 'Задержан'), ('departed', 'Вылетел')], default='scheduled', max_length=12, verbose_name='Статус')),
                ('aircraft', models.CharField(default='Airbus A320', max_length=80, verbose_name='Самолёт')),
                ('capacity', models.PositiveIntegerField(default=180, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество мест')),
                ('price', models.PositiveIntegerField(default=7500, verbose_name='Стоимость, ₽')),
            ],
            options={
                'verbose_name': 'рейс',
                'verbose_name_plural': 'рейсы',
                'ordering': ['departure_at', 'pk'],
                'constraints': [models.UniqueConstraint(fields=('number', 'departure_at'), name='unique_flight_departure')],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_date', models.DateField(verbose_name='Дата рейса')),
                ('text', models.TextField(verbose_name='Ваш отзыв')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Оценка')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='flights.flight', verbose_name='Рейс')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'отзыв',
                'verbose_name_plural': 'отзывы',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passenger_name', models.CharField(max_length=150, verbose_name='Имя и фамилия пассажира')),
                ('seat', models.CharField(max_length=4, verbose_name='Место')),
                ('ticket_number', models.CharField(blank=True, max_length=30, verbose_name='Номер билета')),
                ('checked_in', models.BooleanField(default=False, verbose_name='Зарегистрирован на рейс')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='flights.flight', verbose_name='Рейс')),
            ],
            options={
                'verbose_name': 'бронирование',
                'verbose_name_plural': 'бронирования',
                'ordering': ['-created_at'],
                'constraints': [models.UniqueConstraint(fields=('flight', 'seat'), name='unique_flight_seat'), models.UniqueConstraint(fields=('flight', 'user'), name='unique_user_flight')],
            },
        ),
    ]

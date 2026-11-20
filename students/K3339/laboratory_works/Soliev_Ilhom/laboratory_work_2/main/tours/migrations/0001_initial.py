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
            name='Agency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон')),
                ('email', models.EmailField(max_length=254, verbose_name='Почта')),
            ],
            options={
                'verbose_name': 'турагентство',
                'verbose_name_plural': 'турагентства',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'страна',
                'verbose_name_plural': 'страны',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('start_date', models.DateField(verbose_name='Начало тура')),
                ('end_date', models.DateField(verbose_name='Окончание тура')),
                ('payment_terms', models.TextField(verbose_name='Условия оплаты')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Цена за человека, ₽')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tours.agency', verbose_name='Турагентство')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tours.country', verbose_name='Страна')),
            ],
            options={
                'verbose_name': 'тур',
                'verbose_name_plural': 'туры',
                'ordering': ['start_date', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Начало тура')),
                ('end_date', models.DateField(verbose_name='Окончание тура')),
                ('text', models.TextField(verbose_name='Отзыв')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Оценка')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='tours.tour', verbose_name='Тур')),
            ],
            options={
                'verbose_name': 'отзыв',
                'verbose_name_plural': 'отзывы',
                'ordering': ['-created_at', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('travelers', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)], verbose_name='Количество туристов')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон для связи')),
                ('comment', models.TextField(blank=True, verbose_name='Пожелания')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Цена за человека при бронировании')),
                ('status', models.CharField(choices=[('pending', 'Ожидает подтверждения'), ('confirmed', 'Подтверждено')], default='pending', max_length=12, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата бронирования')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='tours.tour', verbose_name='Тур')),
            ],
            options={
                'verbose_name': 'бронирование',
                'verbose_name_plural': 'бронирования',
                'ordering': ['-created_at', '-pk'],
            },
        ),
        migrations.AddConstraint(
            model_name='tour',
            constraint=models.CheckConstraint(condition=models.Q(('end_date__gte', models.F('start_date'))), name='tour_dates_order'),
        ),
        migrations.AddConstraint(
            model_name='tour',
            constraint=models.CheckConstraint(condition=models.Q(('price__gte', 1)), name='tour_positive_price'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.CheckConstraint(condition=models.Q(('rating__gte', 1), ('rating__lte', 10)), name='review_rating_range'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.CheckConstraint(condition=models.Q(('end_date__gte', models.F('start_date'))), name='review_dates_order'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.UniqueConstraint(fields=('user', 'tour'), name='unique_user_tour_booking'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('travelers__gte', 1), ('travelers__lte', 20)), name='booking_travelers_range'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('unit_price__gte', 1)), name='booking_positive_price'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['pending', 'confirmed'])), name='booking_valid_status'),
        ),
    ]

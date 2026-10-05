import django.conf
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tour",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="Название тура")),
                ("agency", models.CharField(max_length=150, verbose_name="Турагентство")),
                ("country", models.CharField(max_length=100, verbose_name="Страна")),
                ("description", models.TextField(verbose_name="Описание тура")),
                ("start_date", models.DateField(verbose_name="Дата начала")),
                ("end_date", models.DateField(verbose_name="Дата окончания")),
                ("payment_terms", models.TextField(verbose_name="Условия оплаты")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Стоимость")),
            ],
            options={
                "verbose_name": "Тур",
                "verbose_name_plural": "Туры",
                "ordering": ["start_date", "name"],
            },
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tourists_count", models.PositiveIntegerField(default=1, verbose_name="Количество туристов")),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                ("is_confirmed", models.BooleanField(default=False, verbose_name="Подтверждено администратором")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата бронирования")),
                ("tour", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reservations", to="library.tour", verbose_name="Тур")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reservations", to=django.conf.settings.AUTH_USER_MODEL, verbose_name="Пользователь")),
            ],
            options={
                "verbose_name": "Бронирование",
                "verbose_name_plural": "Бронирования",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tour_start_date", models.DateField(verbose_name="Дата начала тура")),
                ("tour_end_date", models.DateField(verbose_name="Дата окончания тура")),
                ("text", models.TextField(verbose_name="Текст комментария")),
                ("rating", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name="Рейтинг")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата комментария")),
                ("tour", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="library.tour", verbose_name="Тур")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to=django.conf.settings.AUTH_USER_MODEL, verbose_name="Комментатор")),
            ],
            options={
                "verbose_name": "Отзыв",
                "verbose_name_plural": "Отзывы",
                "ordering": ["-created_at"],
            },
        ),
    ]

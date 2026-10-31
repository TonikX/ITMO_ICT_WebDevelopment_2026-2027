from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Название")),
            ],
            options={
                "verbose_name": "Страна",
                "verbose_name_plural": "Страны",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="TravelAgency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, verbose_name="Название")),
            ],
            options={
                "verbose_name": "Турагентство",
                "verbose_name_plural": "Турагентства",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Tour",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, verbose_name="Название тура")),
                ("description", models.TextField(verbose_name="Описание")),
                ("start_date", models.DateField(verbose_name="Дата начала")),
                ("end_date", models.DateField(verbose_name="Дата окончания")),
                ("payment_terms", models.TextField(verbose_name="Условия оплаты")),
                (
                    "agency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tours",
                        to="tours.travelagency",
                        verbose_name="Турагентство",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tours",
                        to="tours.country",
                        verbose_name="Страна",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тур",
                "verbose_name_plural": "Туры",
                "ordering": ["start_date"],
            },
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField(verbose_name="Дата начала тура")),
                ("end_date", models.DateField(verbose_name="Дата окончания тура")),
                ("text", models.TextField(verbose_name="Текст отзыва")),
                (
                    "rating",
                    models.IntegerField(
                        validators=[MinValueValidator(1), MaxValueValidator(10)],
                        verbose_name="Оценка",
                    ),
                ),
                (
                    "tour",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="tours.tour",
                        verbose_name="Тур",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
            ],
            options={"verbose_name": "Отзыв", "verbose_name_plural": "Отзывы"},
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_confirmed", models.BooleanField(default=False, verbose_name="Подтверждено")),
                (
                    "tour",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="tours.tour",
                        verbose_name="Тур",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Бронирование",
                "verbose_name_plural": "Бронирования",
            },
        ),
    ]

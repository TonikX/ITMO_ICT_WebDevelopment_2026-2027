import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from library.models import Reservation, Review, Tour


DEMO_TOURS = [
    ("Огни Стамбула", "Турция", 65000, "Прогулки по старому городу и поездка по Босфору."),
    ("Золотое кольцо", "Россия", 42000, "Экскурсии по Суздалю, Владимиру и Ярославлю."),
    ("Винные дороги Кахетии", "Грузия", 68000, "Поездка по винодельням и монастырям Кахетии."),
    ("Сокровища Армении", "Армения", 59000, "Ереван, озеро Севан и храм Гарни."),
    ("Шёлковый путь", "Узбекистан", 79000, "Знакомство с Самаркандом, Бухарой и Хивой."),
    ("Римские каникулы", "Италия", 125000, "Экскурсии по Риму и свободный день для музеев."),
    ("Париж и долина Луары", "Франция", 138000, "Улицы Парижа и замки в долине Луары."),
    ("Берега Каталонии", "Испания", 113000, "Барселона, Жирона и побережье Коста-Брава."),
    ("Остров Крит", "Греция", 97000, "Кносский дворец и отдых на берегу Средиземного моря."),
    ("Долина Нила", "Египет", 89000, "Пирамиды Гизы и храмы Луксора."),
    ("Вкусы Бангкока", "Таиланд", 141000, "Речные рынки, храмы и вечерняя прогулка по городу."),
    ("Киото и Нара", "Япония", 189000, "Сады Киото, исторические кварталы и парк Нары."),
]


class Command(BaseCommand):
    help = "Добавляет демонстрационные туры, пользователей, бронирования и отзывы."

    @transaction.atomic
    def handle(self, *args, **options):
        def demo_password_hash():
            password = os.getenv("DEMO_PASSWORD")
            if not password:
                raise CommandError("Для создания демо-аккаунтов задайте переменную DEMO_PASSWORD.")
            return make_password(password)

        user_model = get_user_model()
        users = []
        for username in ("tour_demo_anna", "tour_demo_ivan", "tour_demo_maria"):
            user, _ = user_model.objects.select_for_update().get_or_create(
                username=username, defaults={"password": demo_password_hash}
            )
            users.append(user)

        first_date = timezone.localdate() + timedelta(days=14)
        for index, (name, country, price, description) in enumerate(DEMO_TOURS):
            tour_fields = {"name": name, "country": country, "agency": "Лаборатория путешествий"}
            tour = Tour.objects.filter(**tour_fields).first()
            if tour is None:
                start_date = first_date + timedelta(days=7 * index)
                tour = Tour.objects.create(
                    **tour_fields,
                    price=price,
                    description=description,
                    start_date=start_date,
                    end_date=start_date + timedelta(days=5),
                    payment_terms="Предоплата 30%, остаток за неделю до выезда.",
                )

            user = users[index % len(users)]
            if not Reservation.objects.filter(tour=tour, user=user).exists():
                Reservation.objects.create(
                    tour=tour,
                    user=user,
                    tourists_count=index % 4 + 1,
                    comment="Демонстрационное бронирование",
                    is_confirmed=index % 4 != 3,
                )
            if not Review.objects.filter(tour=tour, user=user).exists():
                Review.objects.create(
                    tour=tour,
                    user=user,
                    tour_start_date=tour.start_date,
                    tour_end_date=tour.end_date,
                    text=f"Демонстрационный отзыв о туре «{name}».",
                    rating=index % 10 + 1,
                )

        self.stdout.write(self.style.SUCCESS("Демонстрационные данные готовы."))

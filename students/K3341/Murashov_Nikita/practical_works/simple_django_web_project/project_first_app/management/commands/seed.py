import os
import secrets
from datetime import date

from django.core.management.base import BaseCommand

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership

CARS = [
    ("А001АА77", "Toyota", "Camry", "чёрный"),
    ("В222ВВ78", "Lada", "Vesta", "белый"),
    ("С333СС99", "Kia", "Rio", "серый"),
    ("Е444ЕЕ47", "BMW", "X5", "синий"),
]

OWNERS = [
    ("ivanov", "Иван", "Иванов", date(1990, 3, 12), "4510 123456", "Москва, ул. Тверская, 1", "русский"),
    ("petrov", "Пётр", "Петров", date(1985, 7, 25), "4011 654321", "Санкт-Петербург, Невский пр., 10", "русский"),
]

# (владелец, автомобиль, начало, окончание): у каждого >= 3 авто, у одного авто даты не пересекаются
OWNERSHIPS = [
    (0, 0, date(2015, 1, 10), date(2018, 5, 1)),
    (0, 1, date(2018, 6, 1), date(2021, 3, 15)),
    (0, 2, date(2021, 4, 1), None),
    (1, 0, date(2018, 5, 2), None),
    (1, 3, date(2016, 2, 1), date(2020, 12, 31)),
    (1, 1, date(2021, 3, 16), None),
]


def _password(env_name):
    """Пароль из переменной окружения или случайный; в коде паролей нет."""
    return os.environ.get(env_name) or secrets.token_urlsafe(12)


class Command(BaseCommand):
    help = "Практика 1, задание 3: 2 владельца, 4 автомобиля, у каждого владельца >= 3 автомобиля."

    def handle(self, *args, **options):
        created_passwords = []
        user_password = _password("SEED_USER_PASSWORD")
        owners = []
        for username, first, last, birth, passport, address, nation in OWNERS:
            owner, created = CarOwner.objects.get_or_create(
                username=username,
                defaults=dict(
                    first_name=first, last_name=last, birth_date=birth,
                    passport_number=passport, home_address=address, nationality=nation,
                ),
            )
            if created:
                owner.set_password(user_password)
                owner.save()
                created_passwords.append(f"{username} / {user_password}")
                DriverLicense.objects.create(owner=owner, license_number=f"77{owner.pk:08d}", type="B", issue_date=date(2010, 1, 1))
            owners.append(owner)

        cars = [Car.objects.get_or_create(state_number=n, defaults=dict(brand=b, model=m, color=c))[0] for n, b, m, c in CARS]

        for oi, ci, start, end in OWNERSHIPS:
            Ownership.objects.get_or_create(owner=owners[oi], car=cars[ci], start_date=start, defaults={"end_date": end})

        # админ создаётся после владельцев, чтобы /owner/1/ показывал первого владельца
        if not CarOwner.objects.filter(username="admin").exists():
            admin_password = _password("SEED_ADMIN_PASSWORD")
            CarOwner.objects.create_superuser("admin", "admin@example.com", admin_password)
            created_passwords.append(f"admin / {admin_password}")

        if options["verbosity"] > 0:
            self.stdout.write(self.style.SUCCESS("Готово."))
            for line in created_passwords:
                self.stdout.write(f"Создан пользователь (логин / пароль): {line}")

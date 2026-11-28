"""Заполнение базы тестовыми данными: python manage.py seed_owners [--reset]."""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from project_first_app.models import Car, DriverLicense, Owner, Ownership

OWNERS = [
    # username, фамилия, имя, дата рождения, паспорт, адрес, национальность
    ("ivanov", "Иванов", "Пётр", date(1985, 3, 14), "4012 345678", "Санкт-Петербург, Кронверкский пр., 49", "русский"),
    ("petrova", "Петрова", "Анна", date(1990, 7, 2), "4015 112233", "Санкт-Петербург, ул. Ломоносова, 9", "русская"),
    ("sidorov", "Сидоров", "Олег", date(1978, 11, 23), "4009 998877", "Пушкин, ул. Магазейная, 12", "русский"),
    ("karimova", "Каримова", "Лейла", date(1995, 1, 30), "4018 554433", "Колпино, ул. Труда, 3", "татарка"),
    ("melnik", "Мельник", "Андрей", date(1988, 5, 17), "4011 223344", "Гатчина, пр. 25 Октября, 40", "украинец"),
    ("ahmadi", "Ахмади", "Реза", date(1992, 9, 5), "4020 667788", "Санкт-Петербург, Невский пр., 100", "иранец"),
]

CARS = [
    ("А123ВС78", "Toyota", "Camry", "белый"),
    ("К456МН98", "Lada", "Vesta", "серый"),
    ("Е789ОР178", "Kia", "Rio", "красный"),
    ("М321ТУ47", "Hyundai", "Solaris", "синий"),
    ("Н654ХК198", "Skoda", "Octavia", "чёрный"),
    ("О987АВ78", "Volkswagen", "Polo", "серебристый"),
]

# (car index, owner username, начало, конец) — периоды одного авто не пересекаются
OWNERSHIPS = [
    (0, "ivanov", date(2015, 4, 1), date(2018, 6, 30)),
    (0, "petrova", date(2018, 7, 1), date(2021, 3, 31)),
    (0, "ivanov", date(2021, 4, 1), None),
    (1, "petrova", date(2016, 2, 10), date(2019, 9, 1)),
    (1, "ivanov", date(2019, 9, 2), date(2020, 12, 31)),
    (1, "sidorov", date(2021, 1, 1), None),
    (2, "ivanov", date(2012, 5, 5), date(2014, 12, 31)),
    (2, "petrova", date(2015, 1, 1), None),
    (3, "karimova", date(2019, 3, 3), None),
    (4, "melnik", date(2017, 8, 8), date(2022, 8, 7)),
    (4, "ahmadi", date(2022, 8, 8), None),
    (5, "sidorov", date(2014, 6, 1), date(2020, 5, 31)),
    (5, "karimova", date(2020, 6, 1), None),
]

LICENSES = [
    ("ivanov", "7801123456", "B", date(2004, 5, 20)),
    ("petrova", "7802654321", "B", date(2010, 9, 1)),
    ("sidorov", "7803111222", "C", date(1998, 3, 15)),
    ("karimova", "7804333444", "B", date(2015, 6, 10)),
    ("melnik", "7805555666", "BE", date(2008, 2, 28)),
    ("ahmadi", "7806777888", "A", date(2012, 11, 11)),
]


class Command(BaseCommand):
    help = "Создаёт тестовых автовладельцев, автомобили, владения и удостоверения"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="удалить ранее созданные тестовые данные")

    @transaction.atomic
    def handle(self, *args, **options):
        usernames = [o[0] for o in OWNERS]
        if options["reset"]:
            Car.objects.filter(plate_number__in=[c[0] for c in CARS]).delete()
            Owner.objects.filter(username__in=usernames).delete()

        owners = {}
        for username, last, first, born, passport, address, nationality in OWNERS:
            owner, created = Owner.objects.get_or_create(
                username=username,
                defaults={
                    "last_name": last,
                    "first_name": first,
                    "birth_date": born,
                    "passport_number": passport,
                    "home_address": address,
                    "nationality": nationality,
                },
            )
            if created:
                owner.set_unusable_password()  # тестовым владельцам вход не нужен
                owner.save()
            owners[username] = owner

        cars = []
        for plate, brand, model, color in CARS:
            car, _ = Car.objects.get_or_create(
                plate_number=plate, defaults={"brand": brand, "model": model, "color": color}
            )
            cars.append(car)

        for car_index, username, start, end in OWNERSHIPS:
            Ownership.objects.get_or_create(
                car=cars[car_index], owner=owners[username], start_date=start, defaults={"end_date": end}
            )

        for username, number, kind, issued in LICENSES:
            DriverLicense.objects.get_or_create(
                license_number=number,
                defaults={"owner": owners[username], "license_type": kind, "issue_date": issued},
            )

        self.stdout.write(self.style.SUCCESS(
            f"Готово: владельцев {Owner.objects.count()}, автомобилей {Car.objects.count()}, "
            f"владений {Ownership.objects.count()}"
        ))

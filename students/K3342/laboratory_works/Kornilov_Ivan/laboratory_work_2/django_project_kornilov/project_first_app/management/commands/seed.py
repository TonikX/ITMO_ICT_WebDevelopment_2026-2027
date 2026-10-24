from datetime import date

from django.core.management.base import BaseCommand

from project_first_app.models import Car, CarOwner, DrivingLicense, Ownership


OWNERS = [
    {
        'username': 'admin',
        'password': 'admin12345',
        'first_name': 'Иван',
        'last_name': 'Петров',
        'birth_date': date(1990, 5, 12),
        'passport_number': '4010123456',
        'address': 'Санкт-Петербург, Невский пр., 10',
        'nationality': 'российская',
        'is_staff': True,
        'is_superuser': True,
        'license_number': '7711000001',
    },
    {
        'username': 'maria',
        'password': 'owner12345',
        'first_name': 'Мария',
        'last_name': 'Соколова',
        'birth_date': date(1988, 11, 3),
        'passport_number': '4010654321',
        'address': 'Санкт-Петербург, Садовая ул., 4',
        'nationality': 'российская',
        'is_staff': False,
        'is_superuser': False,
        'license_number': '7711000002',
    },
    {
        'username': 'olga',
        'password': 'owner12345',
        'first_name': 'Ольга',
        'last_name': 'Кузнецова',
        'birth_date': date(1995, 2, 20),
        'passport_number': '4008121212',
        'address': 'Москва, Тверская ул., 8',
        'nationality': 'российская',
        'is_staff': False,
        'is_superuser': False,
        'license_number': '7711000003',
    },
    {
        'username': 'sergey',
        'password': 'owner12345',
        'first_name': 'Сергей',
        'last_name': 'Морозов',
        'birth_date': date(1984, 7, 1),
        'passport_number': '4501987654',
        'address': 'Москва, Арбат, 15',
        'nationality': 'российская',
        'is_staff': False,
        'is_superuser': False,
        'license_number': '7711000004',
    },
    {
        'username': 'dmitry',
        'password': 'owner12345',
        'first_name': 'Дмитрий',
        'last_name': 'Волков',
        'birth_date': date(1992, 9, 18),
        'passport_number': '4015777888',
        'address': 'Казань, ул. Баумана, 3',
        'nationality': 'российская',
        'is_staff': False,
        'is_superuser': False,
        'license_number': '7711000005',
    },
]

CARS = [
    ('А123ВС178', 'Lada', 'Vesta', 'белый'),
    ('В456ОР178', 'Toyota', 'Camry', 'чёрный'),
    ('С789ТТ178', 'Kia', 'Rio', 'синий'),
    ('Е111КХ178', 'Hyundai', 'Solaris', 'серебристый'),
    ('К222ММ178', 'Volkswagen', 'Polo', 'красный'),
    ('М333НН178', 'Skoda', 'Octavia', 'серый'),
    ('О444РР178', 'BMW', 'X3', 'чёрный'),
]


class Command(BaseCommand):
    help = 'Заполняет базу владельцами, автомобилями и периодами владения'

    def handle(self, *args, **options):
        owners = {}
        for item in OWNERS:
            owner, created = CarOwner.objects.get_or_create(
                username=item['username'],
                defaults={
                    'first_name': item['first_name'],
                    'last_name': item['last_name'],
                    'birth_date': item['birth_date'],
                    'passport_number': item['passport_number'],
                    'address': item['address'],
                    'nationality': item['nationality'],
                    'is_staff': item['is_staff'],
                    'is_superuser': item['is_superuser'],
                },
            )
            if created:
                owner.set_password(item['password'])
                owner.save()
            owners[item['username']] = owner
            DrivingLicense.objects.get_or_create(
                license_number=item['license_number'],
                defaults={
                    'owner': owner,
                    'license_type': 'B',
                    'issue_date': date(2016, 4, 15),
                },
            )

        cars = {}
        for plate, brand, model_name, color in CARS:
            car, _ = Car.objects.get_or_create(
                license_plate=plate,
                defaults={'brand': brand, 'model_name': model_name, 'color': color},
            )
            cars[plate] = car

        periods = [
            ('admin', 'А123ВС178', date(2019, 1, 1), date(2021, 12, 31)),
            ('maria', 'А123ВС178', date(2022, 1, 15), None),
            ('admin', 'В456ОР178', date(2020, 3, 1), date(2022, 3, 1)),
            ('maria', 'В456ОР178', date(2022, 4, 1), None),
            ('admin', 'С789ТТ178', date(2018, 6, 1), date(2020, 6, 1)),
            ('maria', 'С789ТТ178', date(2020, 7, 1), date(2023, 1, 1)),
            ('olga', 'С789ТТ178', date(2023, 2, 1), None),
            ('maria', 'Е111КХ178', date(2017, 1, 1), date(2019, 1, 1)),
            ('olga', 'К222ММ178', date(2021, 5, 1), None),
            ('sergey', 'М333НН178', date(2019, 8, 1), None),
            ('dmitry', 'О444РР178', date(2020, 1, 10), None),
        ]
        for username, plate, start, end in periods:
            Ownership.objects.get_or_create(
                owner=owners[username],
                car=cars[plate],
                start_date=start,
                defaults={'end_date': end},
            )

        self.stdout.write(self.style.SUCCESS('Данные автовладельцев загружены'))

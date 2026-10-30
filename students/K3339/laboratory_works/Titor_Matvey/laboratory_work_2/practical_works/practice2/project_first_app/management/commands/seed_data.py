
from datetime import date

from django.core.management.base import BaseCommand

from project_first_app.models import Car, Owner, Ownership

OWNERS = [
    ('Иван', 'Иванов', '1990-05-12'),
    ('Мария', 'Петрова', '1992-11-03'),
    ('Пётр', 'Сидоров', '1988-02-28'),
]

CARS = [
    ('Toyota', 'Corolla', 'серебристый', 'A123BC'),
    ('Volkswagen', 'Golf', 'чёрный', 'B456CD'),
    ('Kia', 'Rio', 'белый', 'C789DE'),
]

OWNERSHIPS = [
    (0, 0, '2015-01-01', '2018-01-01'),
    (0, 1, '2016-01-01', '2019-01-01'),
    (1, 0, '2018-01-02', '2021-01-01'),
    (1, 2, '2017-06-01', None),
    (2, 1, '2019-01-02', None),
]

class Command(BaseCommand):
    help = 'Наполняет базу демо-данными: 3 владельца, 3 автомобиля, 5 владений.'

    def handle(self, *args, **options):
        owners = []
        for first, last, birth in OWNERS:
            owner, _ = Owner.objects.update_or_create(
                first_name=first, last_name=last,
                defaults={'birth_date': date.fromisoformat(birth)},
            )
            owners.append(owner)

        cars = []
        for brand, model, color, number in CARS:
            car, _ = Car.objects.update_or_create(
                state_number=number,
                defaults={'brand': brand, 'model': model, 'color': color},
            )
            cars.append(car)

        for owner_index, car_index, start, end in OWNERSHIPS:
            Ownership.objects.update_or_create(
                owner=owners[owner_index],
                car=cars[car_index],
                defaults={
                    'start_date': date.fromisoformat(start),
                    'end_date': date.fromisoformat(end) if end else None,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'OK: владельцев={Owner.objects.count()}, автомобилей={Car.objects.count()}, '
            f'владений={Ownership.objects.count()}'
        ))

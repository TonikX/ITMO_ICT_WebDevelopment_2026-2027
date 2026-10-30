
from datetime import date

from django.core.management.base import BaseCommand

from project_first_app.models import Car, Ownership, User

PEOPLE = [
    ('admin', 'admin123', 'Админ', 'Админов', '0000 000001', 'г. Санкт-Петербург', 'русский', True),
    ('ivan', 'ivan123', 'Иван', 'Иванов', '4015 123456', 'ул. Ленина 1-22', 'русский', False),
    ('maria', 'maria123', 'Мария', 'Петрова', '4019 654321', 'ул. Пушкина 8-5', 'русская', False),
]

CARS = [
    ('Toyota', 'Corolla', 'серебристый', 'A123BC'),
    ('Volkswagen', 'Golf', 'чёрный', 'B456CD'),
]

OWNERSHIPS = [
    ('ivan', 0, '2015-01-01', '2018-01-01'),
    ('ivan', 1, '2016-01-01', None),
    ('maria', 0, '2018-01-02', None),
]

class Command(BaseCommand):
    help = 'Наполняет базу демо-данными (пользователи с паспортом, авто, владения).'

    def handle(self, *args, **options):
        users = []
        for login, password, first, last, passport, address, nat, staff in PEOPLE:
            user, _ = User.objects.get_or_create(username=login)
            user.first_name, user.last_name = first, last
            user.passport_number, user.home_address, user.nationality = passport, address, nat
            user.is_staff = staff
            user.is_superuser = bool(staff)
            user.set_password(password)
            user.save()
            users.append(user)

        cars = []
        for brand, model, color, number in CARS:
            car, _ = Car.objects.update_or_create(
                state_number=number,
                defaults={'brand': brand, 'model': model, 'color': color},
            )
            cars.append(car)

        user_map = {u.username: u for u in users}
        for login, car_index, start, end in OWNERSHIPS:
            Ownership.objects.update_or_create(
                owner=user_map[login],
                car=cars[car_index],
                defaults={
                    'start_date': date.fromisoformat(start),
                    'end_date': date.fromisoformat(end) if end else None,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'OK: пользователей={User.objects.count()}, авто={Car.objects.count()}, '
            f'владений={Ownership.objects.count()}'
        ))

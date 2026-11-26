"""
Данные для практики 2.1, задание 3 (можно ввести и вручную через /admin/):
2 владельца и 4 автомобиля; каждый владелец связан минимум с тремя
автомобилями так, чтобы даты владения одной машиной не пересекались.

    python manage.py seed_practice2
"""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership


class Command(BaseCommand):
    help = 'Практика 2.1: 2 владельца, 4 автомобиля, владения без пересечений'

    @transaction.atomic
    def handle(self, *args, **options):
        anna = CarOwner.objects.create_user(
            username='anna', password='Owner_pass_1', first_name='Анна', last_name='Смирнова',
            birth_date=date(1990, 3, 12), passport_number='4015 111111',
            home_address='Санкт-Петербург, Невский пр., 10', nationality='Россия')
        boris = CarOwner.objects.create_user(
            username='boris', password='Owner_pass_2', first_name='Борис', last_name='Петров',
            birth_date=date(1985, 7, 1), passport_number='4015 222222',
            home_address='Санкт-Петербург, Литейный пр., 5', nationality='Россия')

        DriverLicense.objects.create(owner=anna, number='7800000001', type='B', issue_date=date(2009, 6, 15))
        DriverLicense.objects.create(owner=boris, number='7800000002', type='C', issue_date=date(2004, 2, 20))

        lada = Car.objects.create(license_plate='А001АА78', brand='Lada', model='Vesta', color='Белый')
        kia = Car.objects.create(license_plate='В002ВВ78', brand='Kia', model='Rio', color='Серый')
        vw = Car.objects.create(license_plate='С003СС78', brand='Volkswagen', model='Polo', color='Синий')
        skoda = Car.objects.create(license_plate='Е004ЕЕ78', brand='Skoda', model='Octavia', color='Чёрный')

        # Машина переходит от одного владельца к другому — периоды не пересекаются
        Ownership.objects.create(owner=anna, car=lada, start_date=date(2015, 1, 10), end_date=date(2018, 5, 1))
        Ownership.objects.create(owner=boris, car=lada, start_date=date(2018, 5, 2), end_date=None)
        Ownership.objects.create(owner=anna, car=kia, start_date=date(2018, 6, 1), end_date=date(2021, 2, 1))
        Ownership.objects.create(owner=boris, car=kia, start_date=date(2021, 2, 2), end_date=date(2023, 9, 1))
        Ownership.objects.create(owner=anna, car=vw, start_date=date(2021, 3, 1), end_date=None)
        Ownership.objects.create(owner=boris, car=skoda, start_date=date(2016, 4, 1), end_date=date(2020, 4, 1))
        Ownership.objects.create(owner=anna, car=skoda, start_date=date(2020, 4, 2), end_date=None)

        self.stdout.write(self.style.SUCCESS('Создано: 2 владельца (с удостоверениями), 4 автомобиля, 7 владений'))

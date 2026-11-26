"""
Практика 3.1, задание 2 — запросы на фильтрацию.

    python manage.py practice31_task2

related_name, добавленные в модели:
    Car.owners          -> CarOwner.cars
    Ownership.owner     -> CarOwner.ownerships
    Ownership.car       -> Car.ownerships
    DriverLicense.owner -> CarOwner.licenses
"""
from django.core.management.base import BaseCommand

from project_first_app.models import Car, CarOwner, DriverLicense


class Command(BaseCommand):
    help = 'Практика 3.1, задание 2: фильтрация'

    def show(self, title, code, result):
        self.stdout.write(self.style.MIGRATE_HEADING(f'\n{title}'))
        self.stdout.write(f'>>> {code}')
        self.stdout.write(str(result))

    def handle(self, *args, **options):
        # 1. Все машины марки Toyota
        self.show('1. Все машины марки «Toyota»',
                  "Car.objects.filter(brand='Toyota')",
                  Car.objects.filter(brand='Toyota'))

        # 2. Все водители с именем «Олег»
        self.show('2. Все водители с именем «Олег»',
                  "CarOwner.objects.filter(first_name='Олег')",
                  CarOwner.objects.filter(first_name='Олег'))

        # 3. Случайный владелец -> его id -> удостоверение (2 запроса)
        owner = CarOwner.objects.filter(licenses__isnull=False).order_by('?').first()
        owner_id = owner.id
        self.show('3. Случайный владелец, его id и удостоверение по этому id',
                  "owner_id = CarOwner.objects.filter(licenses__isnull=False).order_by('?').first().id\n"
                  ">>> DriverLicense.objects.get(owner_id=owner_id)",
                  f'owner = {owner}, owner_id = {owner_id}\n'
                  f'{DriverLicense.objects.get(owner_id=owner_id)!r}')

        # 4. Владельцы красных машин (через M:N related_name='cars')
        self.show('4. Все владельцы красных машин',
                  "CarOwner.objects.filter(cars__color='Красный').distinct()",
                  CarOwner.objects.filter(cars__color='Красный').distinct())

        # 5. Владельцы, чей год владения начинается с 2010 (через related_name='ownerships')
        self.show('5. Владельцы, у которых владение машиной началось в 2010 году',
                  'CarOwner.objects.filter(ownerships__start_date__year=2010).distinct()',
                  CarOwner.objects.filter(ownerships__start_date__year=2010).distinct())

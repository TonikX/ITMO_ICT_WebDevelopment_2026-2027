"""
Практика 3.1, задание 1 — создание объектов через ORM.

6–7 новых автовладельцев и 5–6 автомобилей; каждому владельцу —
удостоверение и от 1 до 3 автомобилей (с заполнением ассоциативной сущности
«владение»).

    python manage.py practice31_task1
"""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership


class Command(BaseCommand):
    help = 'Практика 3.1, задание 1: создание владельцев, автомобилей, удостоверений и владений'

    @transaction.atomic
    def handle(self, *args, **options):
        out = self.stdout.write

        # --- 1. Автомобили: .objects.create() ---
        cars = {
            'camry': Car.objects.create(license_plate='К101КК78', brand='Toyota', model='Camry', color='Красный'),
            'corolla': Car.objects.create(license_plate='К102КК78', brand='Toyota', model='Corolla', color='Белый'),
            'solaris': Car.objects.create(license_plate='М201ММ78', brand='Hyundai', model='Solaris', color='Красный'),
            'x5': Car.objects.create(license_plate='Н301НН78', brand='BMW', model='X5', color='Чёрный'),
            'logan': Car.objects.create(license_plate='Р401РР78', brand='Renault', model='Logan', color='Синий'),
            'granta': Car.objects.create(license_plate='Т501ТТ78', brand='Lada', model='Granta', color='Серый'),
        }

        # --- 2. Владельцы: создание объекта класса и .save() ---
        owners_data = [
            ('oleg_i', 'Олег', 'Иванов', date(1980, 1, 15), 'Россия'),
            ('oleg_s', 'Олег', 'Сидоров', date(1992, 6, 3), 'Россия'),
            ('maria', 'Мария', 'Кузнецова', date(1988, 9, 21), 'Россия'),
            ('ivan', 'Иван', 'Попов', date(1975, 12, 2), 'Беларусь'),
            ('elena', 'Елена', 'Васильева', date(1995, 4, 30), 'Россия'),
            ('nguyen', 'Ван', 'Нгуен', date(1999, 8, 8), 'Вьетнам'),
            ('dmitry', 'Дмитрий', 'Морозов', date(1983, 2, 14), 'Казахстан'),
        ]
        owners = []
        for i, (username, first, last, birth, nation) in enumerate(owners_data, start=1):
            owner = CarOwner(username=username, first_name=first, last_name=last,
                             birth_date=birth, nationality=nation,
                             passport_number=f'4020 {100000 + i}',
                             home_address=f'Санкт-Петербург, ул. Примерная, {i}')
            owner.set_password('Owner_pass_31')
            owner.save()
            owners.append(owner)

        # --- 3. Удостоверения: по одному каждому владельцу ---
        issue_dates = [date(2000, 5, 10), date(2012, 3, 1), date(2008, 11, 20), date(1996, 7, 7),
                       date(2015, 9, 9), date(2018, 1, 25), date(2003, 4, 4)]
        for i, (owner, issued) in enumerate(zip(owners, issue_dates), start=1):
            DriverLicense.objects.create(owner=owner, number=f'78{i:02d}{i * 1111:06d}'[:10],
                                         type='B', issue_date=issued)

        # --- 4. Владения: от 1 до 3 автомобилей каждому (заполняем ассоциативную сущность) ---
        plan = [
            (owners[0], [('camry', date(2010, 2, 1), None), ('x5', date(2015, 6, 1), date(2019, 6, 1))]),
            (owners[1], [('solaris', date(2013, 3, 10), None)]),
            (owners[2], [('corolla', date(2010, 8, 15), date(2016, 8, 14)),
                         ('logan', date(2017, 1, 1), None),
                         ('x5', date(2019, 6, 2), None)]),
            (owners[3], [('granta', date(2005, 5, 5), None), ('corolla', date(2016, 8, 15), None)]),
            (owners[4], [('camry', date(2008, 1, 1), date(2010, 1, 31))]),
            (owners[5], [('logan', date(2012, 4, 1), date(2016, 12, 31)), ('solaris', date(2011, 1, 1), date(2013, 3, 9))]),
            (owners[6], [('granta', date(2001, 1, 1), date(2005, 5, 4)), ('x5', date(2010, 9, 1), date(2015, 5, 31))]),
        ]
        for owner, items in plan:
            for key, start, end in items:
                Ownership.objects.create(owner=owner, car=cars[key], start_date=start, end_date=end)

        # --- Отображение созданных объектов ---
        out('Car.objects.all():')
        for car in Car.objects.all():
            out(f'  {car}, цвет: {car.color}')
        out('\nCarOwner.objects.filter(is_superuser=False) — владельцы, удостоверения и автомобили:')
        for owner in CarOwner.objects.filter(is_superuser=False).prefetch_related('licenses', 'cars'):
            licenses = ', '.join(str(l) for l in owner.licenses.all())
            cars_list = ', '.join(str(c) for c in owner.cars.all())
            out(f'  {owner}: удостоверение {licenses or "—"}; авто: {cars_list or "—"}')
        out(self.style.SUCCESS(f'\nВсего владений: {Ownership.objects.count()}'))

"""Практическое задание 1: создание владельцев, удостоверений, автомобилей и владений."""
import os
import sys
from datetime import date

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project_prosvetova.settings')
django.setup()

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership  

OWNERS = [
    ('sokolov_o', 'Олег', 'Соколов', date(1985, 3, 14), '7701100001', 'B', date(2005, 6, 20)),
    ('volkova', 'Елена', 'Волкова', date(1990, 7, 2), '7701100002', 'B', date(2010, 9, 15)),
    ('morozov', 'Дмитрий', 'Морозов', date(1978, 11, 23), '7701100003', 'B,C', date(2001, 4, 10)),
    ('lebedeva', 'Наталья', 'Лебедева', date(1995, 1, 30), '7701100004', 'B', date(2014, 2, 18)),
    ('pavlov', 'Сергей', 'Павлов', date(1982, 5, 9), '7701100005', 'B', date(2003, 8, 25)),
    ('orlova', 'Ирина', 'Орлова', date(1988, 12, 5), '7701100006', 'B', date(2007, 10, 1)),
    ('zaitsev', 'Алексей', 'Зайцев', date(1999, 9, 17), '7701100007', 'B', date(2018, 7, 12)),
]

CARS = [
    ('camry', 'Р101РР197', 'Toyota', 'Camry', 'красный'),
    ('rav4', 'Т202ТТ197', 'Toyota', 'RAV4', 'белый'),
    ('sportage', 'К303КК178', 'Kia', 'Sportage', 'чёрный'),
    ('polo', 'Х404ХХ178', 'Volkswagen', 'Polo', 'красный'),
    ('rapid', 'М505ММ47', 'Skoda', 'Rapid', 'серый'),
    ('qashqai', 'Н606НН47', 'Nissan', 'Qashqai', 'серебристый'),
]

OWNERSHIPS = [
    ('sokolov_o', 'camry', date(2010, 5, 1), date(2014, 4, 30)),
    ('sokolov_o', 'rav4', date(2014, 5, 1), date(2022, 12, 31)),
    ('volkova', 'camry', date(2014, 5, 1), date(2019, 12, 31)),
    ('volkova', 'polo', date(2012, 3, 10), date(2019, 8, 31)),
    ('morozov', 'camry', date(2020, 1, 15), None),
    ('morozov', 'sportage', date(2016, 6, 1), None),
    ('morozov', 'rapid', date(2011, 2, 20), date(2015, 12, 31)),
    ('lebedeva', 'polo', date(2019, 9, 1), None),
    ('pavlov', 'sportage', date(2012, 8, 1), date(2016, 5, 31)),
    ('pavlov', 'rapid', date(2016, 1, 1), None),
    ('pavlov', 'qashqai', date(2015, 4, 1), date(2021, 3, 31)),
    ('orlova', 'qashqai', date(2021, 4, 1), None),
]

owners, licenses = {}, []
for username, first, last, birth, number, lic_type, issued in OWNERS:
    owner = CarOwner.objects.filter(username=username).first()
    if owner is None:
        # Способ 1: экземпляр модели + save()
        owner = CarOwner(username=username, first_name=first, last_name=last, birth_date=birth)
        owner.set_unusable_password()
        owner.save()
    owners[username] = owner
    # Способ 2: objects.create (через get_or_create — повторный запуск не дублирует)
    lic, _ = DriverLicense.objects.get_or_create(
        license_number=number, defaults={'owner': owner, 'type': lic_type, 'issue_date': issued})
    licenses.append(lic)

cars = {}
for key, plate, brand, model, color in CARS:
    cars[key], _ = Car.objects.get_or_create(
        plate_number=plate, defaults={'brand': brand, 'model': model, 'color': color})

ownerships = []
for username, car_key, start, end in OWNERSHIPS:
    o, _ = Ownership.objects.get_or_create(
        owner=owners[username], car=cars[car_key], defaults={'start_date': start, 'end_date': end})
    ownerships.append(o)

# .add() по M2M: промежуточная сущность Ownership заполняется через through_defaults
zaitsev, rav4 = owners['zaitsev'], cars['rav4']
if not zaitsev.cars.filter(pk=rav4.pk).exists():
    zaitsev.cars.add(rav4, through_defaults={'start_date': date(2023, 1, 10)})
ownerships.append(Ownership.objects.get(owner=zaitsev, car=rav4))

print('=== Владельцы ===')
for o in owners.values():
    print(o)
print('\n=== Автомобили ===')
for c in cars.values():
    print(c)
print('\n=== Водительские удостоверения ===')
for lic in licenses:
    print(lic)
print('\n=== Владения ===')
for o in ownerships:
    print(o)

print('\n=== Сводка по владельцам ===')
for o in owners.values():
    lic = o.licenses.first()
    print(f'{o}: удостоверение {lic.license_number}; авто: {", ".join(str(c) for c in o.cars.all())}')

print(f'\nСоздано/найдено: владельцев {len(owners)}, автомобилей {len(cars)}, '
      f'удостоверений {len(licenses)}, владений {len(ownerships)}')

totals = (CarOwner.objects.count(), Car.objects.count(), Ownership.objects.count(), DriverLicense.objects.count())
print(f'Всего в БД: владельцев {totals[0]}, автомобилей {totals[1]}, владений {totals[2]}, удостоверений {totals[3]}')


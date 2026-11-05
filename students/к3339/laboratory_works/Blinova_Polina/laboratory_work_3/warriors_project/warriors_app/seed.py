import os
import sys
import django
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warriors_project.settings')
django.setup()

from warriors_app.models import CarOwner, Car, Ownership, DriverLicense



def run():
    owners_data = [
        ('Иванов', 'Иван', datetime(1990, 1, 1)),
        ('Петров', 'Олег', datetime(1985, 5, 12)),
        ('Сидорова', 'Анна', datetime(1995, 8, 23)),
        ('Николаев', 'Олег', datetime(1978, 3, 4)),
        ('Кузнецов', 'Дмитрий', datetime(2000, 11, 30)),
        ('Смирнова', 'Елена', datetime(1992, 6, 15)),
        ('Фёдоров', 'Олег', datetime(1988, 9, 9)),
    ]
    owners = [
        CarOwner.objects.create(last_name=ln, first_name=fn, birth_date=bd)
        for ln, fn, bd in owners_data
    ]

    cars_data = [
        ('A001AA', 'Toyota', 'Camry', 'красный'),
        ('A002BB', 'Toyota', 'Corolla', 'белый'),
        ('B003CC', 'BMW', 'X5', 'чёрный'),
        ('K004DD', 'Kia', 'Rio', 'красный'),
        ('L005EE', 'Lada', 'Vesta', 'серый'),
    ]
    cars = [
        Car.objects.create(state_number=sn, brand=b, model=m, color=c)
        for sn, b, m, c in cars_data
    ]

    for i, owner in enumerate(owners, start=1):
        DriverLicense.objects.create(
            owner=owner,
            license_number=f'LIC{i:07d}',
            license_type='B',
            issue_date=datetime(2010 + i, 1, 1),
        )

    ownership_plan = [
        (owners[0], cars[0], datetime(2010, 5, 1)),
        (owners[0], cars[1], datetime(2012, 6, 1)),
        (owners[1], cars[2], datetime(2015, 7, 1)),
        (owners[2], cars[3], datetime(2011, 8, 1)),
        (owners[3], cars[0], datetime(2013, 9, 1)),
        (owners[4], cars[4], datetime(2010, 10, 1)),
        (owners[5], cars[1], datetime(2016, 11, 1)),
        (owners[6], cars[3], datetime(2014, 12, 1)),
        (owners[6], cars[2], datetime(2017, 1, 15)),
    ]
    for owner, car, start in ownership_plan:
        Ownership.objects.create(owner=owner, car=car, start_date=start)

    print('Создано:')
    print('владельцев:', CarOwner.objects.count())
    print('авто:', Car.objects.count())
    print('владений:', Ownership.objects.count())
    print('удостоверений:', DriverLicense.objects.count())


if __name__ == '__main__':
    run()
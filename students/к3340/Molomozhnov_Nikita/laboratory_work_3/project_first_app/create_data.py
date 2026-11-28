import os
import django
from datetime import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project_molomozhnov.settings')
django.setup()

from project_first_app.models import CarOwner, Car, Ownership, DriverLicense

owners = list(CarOwner.objects.all())

if not owners:
    print("Нет владельцев — создай их через админку или добавь вручную")
    exit()

cars_data = [
    ("A123BC", "Toyota", "Camry", "red"),
    ("B456DE", "Toyota", "Corolla", "white"),
    ("C789FG", "BMW", "X5", "black"),
    ("D321HI", "Lada", "Vesta", "red"),
    ("E654JK", "Kia", "Rio", "blue"),
]

cars = []
for num, brand, model, color in cars_data:
    c, _ = Car.objects.get_or_create(
        state_number=num,
        defaults={"brand": brand, "model_name": model, "color": color},
    )
    cars.append(c)

def aware(y, m, d, h=0):
    return timezone.make_aware(datetime(y, m, d, h, 0))

licenses_data = [
    ("AA111111", "B", aware(2005, 6, 1, 10)),
    ("BB222222", "B", aware(2010, 8, 15, 10)),
    ("CC333333", "C", aware(2000, 2, 20, 10)),
    ("DD444444", "B", aware(2015, 5, 10, 10)),
    ("EE555555", "B", aware(2008, 11, 3, 10)),
    ("FF666666", "C", aware(2012, 9, 27, 10)),
]

for owner, (num, ltype, issued) in zip(owners, licenses_data):
    DriverLicense.objects.update_or_create(
        owner=owner,
        defaults={"license_number": num, "license_type": ltype, "issue_date": issued},
    )

ownership_plan = [
    (owners[0], cars[0], aware(2010, 5, 1)),
    (owners[0], cars[1], aware(2015, 6, 10)),
    (owners[1], cars[2], aware(2012, 3, 15)),
    (owners[2], cars[3], aware(2011, 7, 20)),
    (owners[3], cars[4], aware(2019, 9, 1)),
    (owners[4], cars[0], aware(2018, 2, 11)),
    (owners[5], cars[1], aware(2016, 8, 23)),
]

for owner, car, start in ownership_plan:
    Ownership.objects.get_or_create(
        owner=owner, car=car, defaults={"start_date": start}
    )

print("Cars:", Car.objects.count())
print("Ownerships:", Ownership.objects.count())
print("Licenses:", DriverLicense.objects.count())
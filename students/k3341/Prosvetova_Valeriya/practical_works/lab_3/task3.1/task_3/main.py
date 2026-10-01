"""Практическое задание 3: агрегация и аннотация."""
import os
import sys
from datetime import date

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project_prosvetova.settings')
django.setup()

from django.db.models import Count, F, Max, Min 

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership  

print("1. DriverLicense.objects.aggregate(oldest=Min('issue_date'))")
oldest = DriverLicense.objects.aggregate(oldest=Min('issue_date'))
print(oldest, '\n')

print("2. Ownership.objects.filter(car__model='Camry').aggregate(latest=Max('start_date'))")
latest = Ownership.objects.filter(car__model='Camry').aggregate(latest=Max('start_date'))
print(latest, '\n')

print("3. CarOwner.objects.annotate(car_count=Count('cars', distinct=True))")
per_owner = CarOwner.objects.annotate(car_count=Count('cars', distinct=True)).order_by('id')
for o in per_owner:
    print(f'   {o.username:<10} {o}: {o.car_count}')
print()

print("4. Car.objects.values('brand').annotate(n=Count('id')).order_by('brand')")
per_brand = Car.objects.values('brand').annotate(n=Count('id')).order_by('brand')
for row in per_brand:
    print(f"   {row['brand']}: {row['n']}")
print()

print("5. CarOwner.objects.order_by(F('licenses__issue_date').asc(nulls_last=True)).distinct()")
for o in CarOwner.objects.order_by(F('licenses__issue_date').asc(nulls_last=True)).distinct():
    lic = o.licenses.first()
    print(f'   {o} — {lic.issue_date if lic else "нет удостоверения"}')



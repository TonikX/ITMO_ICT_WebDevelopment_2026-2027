"""Практическое задание 2: фильтрация."""
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project_prosvetova.settings')
django.setup()

from project_first_app.models import Car, CarOwner, DriverLicense  

print("1. related_name: Ownership.owner/car -> 'ownerships', DriverLicense.owner -> 'licenses' "
      "(models.py + миграция 0002)\n")

print("2. Car.objects.filter(brand='Toyota')")
toyotas = Car.objects.filter(brand='Toyota')
print(toyotas, '\n')

print("3. CarOwner.objects.filter(first_name='Олег')")
olegs = CarOwner.objects.filter(first_name='Олег')
print(olegs, '\n')

print("4. owner = CarOwner.objects.filter(licenses__isnull=False).order_by('?').first()")
owner = CarOwner.objects.filter(licenses__isnull=False).order_by('?').first()
print(f'   {owner}, id = {owner.id}')
print("   DriverLicense.objects.get(owner_id=owner.id)")
lic = DriverLicense.objects.get(owner_id=owner.id)
print(f'   {lic}\n')

print("5. CarOwner.objects.filter(cars__color='красный').distinct()")
red = CarOwner.objects.filter(cars__color='красный').distinct()
print(red, '\n')

print("6. CarOwner.objects.filter(ownerships__start_date__year=2010).distinct()")
y2010 = CarOwner.objects.filter(ownerships__start_date__year=2010).distinct()
print(y2010)


import os
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project_stepanova.settings')
django.setup()

# Ваш оригинальный код:
import random
from datetime import date
from project_first_app.models import User, Car, DrivingLicence, Ownership

users = User.objects.all()
cars = list(Car.objects.all())

# 1. Создаем удостоверения всем, у кого их еще нет
for i, user in enumerate(users):
    DrivingLicence.objects.get_or_create(owner=user, defaults={"license_number": f"9900{i}{random.randint(10, 99)}", "type": "B", "date": date(2020, 1, 1)})

# 2. Оформляем владение (каждому достанется от 1 до 3 случайных машин)
for user in users:
    assigned = random.sample(cars, random.randint(1, min(3, len(cars))))
    for car in assigned:
        Ownership.objects.get_or_create(owner=user, car=car, defaults={"date_start": date(2023, 5, 1)})

# 3. Выводим итоговый результат
print('Результат:')
for ow in Ownership.objects.all():
    print(f"{ow.owner} -> {ow.car.brand} {ow.car.model} [{ow.car.license_plate}]")

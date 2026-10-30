from datetime import datetime

from django.db.models import Count, Max, Min
from django.utils import timezone

from project_first_app.models import (
    Car,
    CarOwner,
    DriverLicense,
    Ownership,
)


def date(year, month, day):
    return timezone.make_aware(datetime(year, month, day))


print("\n 1. создание объектов")

owners_data = [
    ("ivan_petrov", "Иван", "Петров", 1995, 5, 12, "4010123456", "Санкт-Петербург", "Русский"),
    ("anna_smirnova", "Анна", "Смирнова", 1998, 3, 20, "4010234567", "Москва", "Русская"),
    ("oleg_ivanov", "Олег", "Иванов", 1990, 7, 15, "4010345678", "Казань", "Русский"),
    ("maria_kuznetsova", "Мария", "Кузнецова", 2000, 11, 8, "4010456789", "Санкт-Петербург", "Русская"),
    ("dmitry_sokolov", "Дмитрий", "Соколов", 1987, 2, 25, "4010567890", "Новосибирск", "Русский"),
    ("elena_orlova", "Елена", "Орлова", 1996, 9, 10, "4010678901", "Екатеринбург", "Русская"),
    ("alexey_volkov", "Алексей", "Волков", 1993, 12, 5, "4010789012", "Самара", "Русский"),
]

for username, first_name, last_name, year, month, day, passport, address, nationality in owners_data:
    if not CarOwner.objects.filter(username=username).exists():
        CarOwner.objects.create_user(
            username=username,
            password="password123",
            first_name=first_name,
            last_name=last_name,
            birth_date=date(year, month, day),
            passport_number=passport,
            home_address=address,
            nationality=nationality,
        )


cars_data = [
    ("А123ВС178", "Toyota", "Camry", "Красный"),
    ("В456ОР777", "BMW", "X5", "Черный"),
    ("С789КМ178", "Toyota", "Corolla", "Белый"),
    ("Е321АН799", "Kia", "Rio", "Красный"),
    ("М654ТР178", "Hyundai", "Solaris", "Синий"),
    ("Н987УК777", "BMW", "320i", "Серый"),
]

for plate, brand, model, color in cars_data:
    Car.objects.get_or_create(
        license_plate=plate,
        defaults={
            "brand": brand,
            "model": model,
            "color": color,
        },
    )


licenses_data = [
    ("ivan_petrov", "7800123456", 2015, 5, 12),
    ("anna_smirnova", "7800234567", 2018, 3, 20),
    ("oleg_ivanov", "7800345678", 2010, 7, 15),
    ("maria_kuznetsova", "7800456789", 2020, 11, 8),
    ("dmitry_sokolov", "7800567890", 2008, 2, 25),
    ("elena_orlova", "7800678901", 2016, 9, 10),
    ("alexey_volkov", "7800789012", 2013, 12, 5),
]

for username, number, year, month, day in licenses_data:
    owner = CarOwner.objects.get(username=username)

    DriverLicense.objects.get_or_create(
        number=number,
        defaults={
            "owner": owner,
            "license_type": "B",
            "issue_date": date(year, month, day),
        },
    )


ownership_data = [
    ("ivan_petrov", "А123ВС178", (2015, 6, 10), None),
    ("ivan_petrov", "В456ОР777", (2020, 3, 15), None),
    ("anna_smirnova", "С789КМ178", (2018, 4, 20), None),
    ("oleg_ivanov", "Е321АН799", (2010, 7, 12), None),
    ("oleg_ivanov", "М654ТР178", (2017, 9, 1), None),
    ("maria_kuznetsova", "Н987УК777", (2021, 2, 14), None),
    ("dmitry_sokolov", "А123ВС178", (2009, 5, 10), (2014, 12, 31)),
    ("elena_orlova", "В456ОР777", (2016, 8, 20), (2020, 1, 15)),
    ("alexey_volkov", "С789КМ178", (2013, 11, 5), (2017, 6, 10)),
]

for username, plate, start, end in ownership_data:
    owner = CarOwner.objects.get(username=username)
    car = Car.objects.get(license_plate=plate)

    Ownership.objects.get_or_create(
        owner=owner,
        car=car,
        start_date=date(*start),
        defaults={
            "end_date": date(*end) if end else None,
        },
    )


print("\nАвтовладельцы:")
for owner in CarOwner.objects.all():
    print(owner)

print("\nАвтомобили:")
for car in Car.objects.all():
    print(car)

print("\nВодительские удостоверения:")
for license in DriverLicense.objects.select_related("owner"):
    print(license.owner, "-", license.number)

print("\nСвязи владельцев с автомобилями:")
for owner in CarOwner.objects.all():
    print(owner, "-", list(owner.cars.all()))



print("\n2. фильтрация")

# Все автомобили марки Toyota
print("\n1. Автомобили Toyota:")
print(Car.objects.filter(brand="Toyota"))

# Все водители с именем Олег
print("\n2. Водители с именем Олег:")
print(CarOwner.objects.filter(first_name="Олег"))

# Получение водительского удостоверения по ID владельца
print("\n3. Удостоверение владельца по ID:")
owner = CarOwner.objects.get(username="oleg_ivanov")
print("ID владельца:", owner.id)
print(DriverLicense.objects.get(owner_id=owner.id))

# Владельцы красных автомобилей
print("\n4. Владельцы красных автомобилей:")
print(CarOwner.objects.filter(cars__color="Красный").distinct())

# Владельцы, начавшие владеть автомобилем в 2010 году
print("\n5. Владельцы автомобилей с 2010 года:")
print(
    CarOwner.objects.filter(
        ownership__start_date__year=2010
    ).distinct()
)




print("\n3. агрегация и аннотация ")

# 1. Самая ранняя дата выдачи удостоверения
print("\n1. Самая ранняя дата выдачи удостоверения:")
print(
    DriverLicense.objects.aggregate(
        earliest_date=Min("issue_date")
    )
)

print("\n2. Самая поздняя дата начала владения Toyota Camry:")
print(
    Ownership.objects.filter(
        car__model="Camry"
    ).aggregate(
        latest_date=Max("start_date")
    )
)

print("\n3. Количество автомобилей у каждого владельца:")

owners = CarOwner.objects.annotate(
    car_count=Count("cars", distinct=True)
)

for owner in owners:
    print(owner, "-", owner.car_count)

print("\n4. Количество автомобилей каждой марки:")

brands = Car.objects.values("brand").annotate(
    car_count=Count("id")
)

for brand in brands:
    print(brand["brand"], "-", brand["car_count"])

print("\n5. Владельцы по дате выдачи удостоверения:")

owners = CarOwner.objects.order_by(
    "driverlicense__issue_date"
).distinct()

for owner in owners:
    print(owner)
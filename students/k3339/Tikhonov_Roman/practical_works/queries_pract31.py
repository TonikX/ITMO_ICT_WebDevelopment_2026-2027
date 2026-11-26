import datetime

from django.db.models import Count, Max, Min

from project_first_app.models import Car, DriverLicense, Ownership, User

CARS = [
    ("а111вг31", "Toyota", "Camry", "красный"),
    ("е222жз31", "Ford", "Focus", "серый"),
    ("в333ии31", "Lada", "Vesta", "белый"),
    ("н444кл31", "BMW", "X5", "чёрный"),
    ("м555но31", "Kia", "Rio", "красный"),
    ("о666пр31", "Skoda", "Octavia", "синий"),
]

OWNERS = [
    ("pr31_ivanov", "Иванов", "Пётр", datetime.date(1985, 3, 12)),
    ("pr31_smirnova", "Смирнова", "Анна", datetime.date(1990, 7, 25)),
    ("pr31_kuznetsov", "Кузнецов", "Олег", datetime.date(1988, 11, 2)),
    ("pr31_popova", "Попова", "Мария", datetime.date(1992, 4, 18)),
    ("pr31_vasiliev", "Васильев", "Сергей", datetime.date(1983, 9, 30)),
    ("pr31_morozova", "Морозова", "Ольга", datetime.date(1995, 1, 8)),
]

OWNERSHIPS = [
    ("pr31_ivanov", "а111вг31", datetime.date(2010, 5, 1), datetime.date(2014, 12, 20)),
    ("pr31_ivanov", "е222жз31", datetime.date(2015, 1, 1), None),
    ("pr31_smirnova", "а111вг31", datetime.date(2015, 2, 10), datetime.date(2019, 7, 1)),
    ("pr31_smirnova", "в333ии31", datetime.date(2019, 8, 1), None),
    ("pr31_kuznetsov", "н444кл31", datetime.date(2012, 3, 15), None),
    ("pr31_kuznetsov", "о666пр31", datetime.date(2020, 1, 10), datetime.date(2020, 12, 15)),
    ("pr31_kuznetsov", "м555но31", datetime.date(2022, 5, 20), None),
    ("pr31_popova", "е222жз31", datetime.date(2016, 4, 1), datetime.date(2020, 11, 30)),
    ("pr31_vasiliev", "о666пр31", datetime.date(2021, 6, 1), None),
    ("pr31_morozova", "в333ии31", datetime.date(2013, 9, 10), datetime.date(2017, 2, 28)),
]

LICENSES = [
    ("pr31_ivanov", "3110234567", "B", datetime.date(2008, 4, 15)),
    ("pr31_ivanov", "3111298765", "C", datetime.date(2014, 5, 22)),
    ("pr31_smirnova", "3120345678", "B", datetime.date(2012, 6, 20)),
    ("pr31_kuznetsov", "3130456789", "B", datetime.date(2010, 8, 5)),
    ("pr31_popova", "3140567890", "B", datetime.date(2015, 3, 9)),
    ("pr31_vasiliev", "3150678901", "B", datetime.date(2006, 11, 12)),
    ("pr31_morozova", "3160789012", "B", datetime.date(2018, 7, 3)),
]

User.objects.exclude(is_superuser=True).delete()
Car.objects.all().delete()

users = {username: User.objects.create(
    username=username, last_name=last_name, first_name=first_name, birth_date=birth_date
) for username, last_name, first_name, birth_date in OWNERS}

cars = {number: Car.objects.create(
    state_number=number, brand=brand, model=model, color=color
) for number, brand, model, color in CARS}

for username, number, start, end in OWNERSHIPS:
    Ownership.objects.create(owner=users[username], car=cars[number], start_date=start, end_date=end)

for username, number, license_type, issued in LICENSES:
    DriverLicense.objects.create(
        owner=users[username], license_number=number, license_type=license_type, issue_date=issued
    )

print("=" * 70)
print("Практическое задание 1. Создание объектов")
print("=" * 70)
for owner in User.objects.filter(username__startswith="pr31_").order_by("pk"):
    licenses = ", ".join(str(dl) for dl in owner.driverlicense_set.all())
    print(owner, "| удостоверения:", licenses or "-", "| машины:", ", ".join(str(car) for car in owner.cars.all()))
print("Владельцев:", User.objects.filter(username__startswith="pr31_").count(),
      "| Автомобилей:", Car.objects.count(),
      "| Владений:", Ownership.objects.count(),
      "| Удостоверений:", DriverLicense.objects.count())

print()
print("=" * 70)
print("Практическое задание 2. Запросы на фильтрацию")
print("=" * 70)

print("\n1) Все машины марки Toyota:")
for car in Car.objects.filter(brand="Toyota"):
    print("   ", car, "|", car.state_number, "|", car.color)

print("\n2) Все водители с именем Олег:")
for owner in User.objects.filter(first_name="Олег"):
    print("   ", owner)

print("\n3) Удостоверение владельца по его id (в 2 запроса):")
owner_id = User.objects.filter(username="pr31_vasiliev").values("id").first()["id"]
print("    id владельца:", owner_id)
dl = DriverLicense.objects.get(owner_id=owner_id)
print("   ", dl)

print("\n4) Все владельцы красных машин:")
for owner in User.objects.filter(cars__color="красный").distinct():
    print("   ", owner)

print("\n5) Все владельцы, чей год владения машиной начинается с 2010:")
for owner in User.objects.filter(ownership__start_date__year=2010).distinct():
    print("   ", owner)

print()
print("=" * 70)
print("Практическое задание 3. Агрегация и аннотация запросов")
print("=" * 70)

print("\n1) Дата выдачи самого старшего водительского удостоверения:")
print("   ", DriverLicense.objects.aggregate(oldest=Min("issue_date")))

print("\n2) Самая поздняя дата владения по каждой из существующих моделей машин:")
for row in Ownership.objects.values("car__model").annotate(latest=Max("end_date")):
    print("   ", row["car__model"], "->", row["latest"])

print("\n3) Количество машин для каждого водителя:")
for owner in User.objects.filter(username__startswith="pr31_").annotate(cars_total=Count("cars")):
    print("   ", owner, "->", owner.cars_total)

print("\n4) Количество машин каждой марки:")
for row in Car.objects.values("brand").annotate(total=Count("id")):
    print("   ", row["brand"], "->", row["total"])

print("\n5) Владельцы, отсортированные по дате выдачи удостоверения:")
for owner in User.objects.filter(username__startswith="pr31_").annotate(first_license=Min("driverlicense__issue_date")).order_by("first_license"):
    print("   ", owner, "|", owner.first_license)

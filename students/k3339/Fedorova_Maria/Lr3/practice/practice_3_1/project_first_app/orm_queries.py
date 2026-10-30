from datetime import date

from django.db.models import Count, Max, Min

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership

CarOwner.objects.all().delete()
Car.objects.all().delete()

owners = [
    CarOwner.objects.create(
        first_name="Олег",
        last_name="Иванов",
        birth_date=date(1985, 3, 12),
    ),
    CarOwner.objects.create(
        first_name="Анна",
        last_name="Петрова",
        birth_date=date(1990, 7, 21),
    ),
    CarOwner.objects.create(
        first_name="Дмитрий",
        last_name="Сидоров",
        birth_date=date(1988, 1, 5),
    ),
    CarOwner.objects.create(
        first_name="Мария",
        last_name="Кузнецова",
        birth_date=date(1995, 11, 30),
    ),
    CarOwner.objects.create(
        first_name="Олег",
        last_name="Смирнов",
        birth_date=date(1982, 9, 8),
    ),
    CarOwner.objects.create(
        first_name="Елена",
        last_name="Волкова",
        birth_date=date(1993, 4, 17),
    ),
    CarOwner.objects.create(
        first_name="Игорь",
        last_name="Морозов",
        birth_date=date(1987, 12, 2),
    ),
]

cars = [
    Car.objects.create(
        state_number="A111AA178",
        brand="Toyota",
        model="Camry",
        color="чёрный",
    ),
    Car.objects.create(
        state_number="B222BB178",
        brand="Toyota",
        model="Corolla",
        color="красный",
    ),
    Car.objects.create(
        state_number="C333CC178",
        brand="BMW",
        model="X5",
        color="белый",
    ),
    Car.objects.create(
        state_number="E444EE178",
        brand="Lada",
        model="Vesta",
        color="синий",
    ),
    Car.objects.create(
        state_number="H555HH178",
        brand="Kia",
        model="Rio",
        color="красный",
    ),
    Car.objects.create(
        state_number="K666KK178",
        brand="Honda",
        model="Civic",
        color="серый",
    ),
]

ownership_links = [
    (0, 0, date(2010, 1, 15), date(2015, 6, 1)),
    (0, 1, date(2016, 3, 1), None),
    (1, 1, date(2012, 5, 10), date(2018, 1, 1)),
    (1, 4, date(2018, 2, 1), None),
    (2, 2, date(2009, 8, 20), date(2014, 8, 20)),
    (2, 0, date(2015, 9, 1), None),
    (2, 5, date(2020, 1, 1), None),
    (3, 3, date(2011, 4, 4), None),
    (4, 4, date(2010, 11, 11), date(2019, 11, 11)),
    (4, 2, date(2019, 12, 1), None),
    (5, 5, date(2013, 7, 7), None),
    (6, 3, date(2017, 6, 1), None),
    (6, 1, date(2021, 1, 15), None),
]

for owner_idx, car_idx, start, end in ownership_links:
    Ownership.objects.create(
        owner=owners[owner_idx],
        car=cars[car_idx],
        start_date=start,
        end_date=end,
    )

licenses = [
    DriverLicense.objects.create(
        owner=owners[0],
        license_number="78AA100001",
        license_type="B",
        issue_date=date(2008, 5, 1),
    ),
    DriverLicense.objects.create(
        owner=owners[1],
        license_number="78BB100002",
        license_type="B",
        issue_date=date(2011, 3, 15),
    ),
    DriverLicense.objects.create(
        owner=owners[2],
        license_number="78CC100003",
        license_type="C",
        issue_date=date(2005, 9, 20),
    ),
    DriverLicense.objects.create(
        owner=owners[3],
        license_number="78DD100004",
        license_type="B",
        issue_date=date(2014, 1, 10),
    ),
    DriverLicense.objects.create(
        owner=owners[4],
        license_number="78EE100005",
        license_type="B",
        issue_date=date(2007, 12, 12),
    ),
    DriverLicense.objects.create(
        owner=owners[5],
        license_number="78FF100006",
        license_type="B",
        issue_date=date(2012, 8, 8),
    ),
    DriverLicense.objects.create(
        owner=owners[6],
        license_number="78GG100007",
        license_type="B",
        issue_date=date(2016, 4, 4),
    ),
]

print("=== Задача 1: созданные объекты ===")
print("Владельцы:", list(CarOwner.objects.all()))
print("Автомобили:", list(Car.objects.all()))
print("Владения:", list(Ownership.objects.all()))
print("Удостоверения:", list(DriverLicense.objects.all()))

print("\n=== Задача 2: фильтрация ===")

toyota_cars = Car.objects.filter(brand="Toyota")
print("1) Машины марки Toyota:", list(toyota_cars))

oleg_owners = CarOwner.objects.filter(first_name="Олег")
print("2) Водители с именем Олег:", list(oleg_owners))

random_owner = CarOwner.objects.first()
owner_id = random_owner.id
license_obj = DriverLicense.objects.get(owner_id=owner_id)
print(f"3) Удостоверение владельца id={owner_id}:", license_obj)

red_owners = CarOwner.objects.filter(cars__color="красный").distinct()
print("4) Владельцы красных машин:", list(red_owners))

owners_2010 = CarOwner.objects.filter(
    ownerships__start_date__year=2010,
).distinct()
print("5) Владельцы с годом начала владения 2010:", list(owners_2010))

print("\n=== Задача 3: агрегация ===")

oldest_license = DriverLicense.objects.aggregate(oldest=Min("issue_date"))
print("1) Самая ранняя дата выдачи удостоверения:", oldest_license)

latest_ownership = Ownership.objects.filter(car__model="Camry").aggregate(
    latest=Max("start_date"),
)
print("2) Самая поздняя дата владения для модели Camry:", latest_ownership)

cars_per_owner = CarOwner.objects.annotate(cars_count=Count("cars"))
print("3) Количество машин у каждого владельца:")
for owner in cars_per_owner:
    print(f"   {owner}: {owner.cars_count}")

cars_per_brand = Car.objects.values("brand").annotate(count=Count("id"))
print("4) Количество машин каждой марки:", list(cars_per_brand))

owners_by_license = (
    CarOwner.objects.filter(licenses__isnull=False)
    .order_by("licenses__issue_date")
    .distinct()
)
print("5) Автовладельцы по дате выдачи удостоверения:")
for owner in owners_by_license:
    lic = owner.licenses.order_by("issue_date").first()
    print(f"   {owner} — {lic.issue_date if lic else None}")

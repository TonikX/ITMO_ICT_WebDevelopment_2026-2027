from datetime import date

from django.core.management.base import BaseCommand
from django.db.models import Count, Max, Min

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership


class Command(BaseCommand):
    help = "Практика 3.1: создание объектов, фильтры, агрегация"

    def handle(self, *args, **options):
        self.stdout.write("=== Практическое задание 1: создание объектов ===")
        owners_data = [
            ("owner1", "Олег", "Иванов", "1990-01-15"),
            ("owner2", "Мария", "Петрова", "1992-03-20"),
            ("owner3", "Олег", "Сидоров", "1988-07-08"),
            ("owner4", "Анна", "Козлова", "1995-11-02"),
            ("owner5", "Игорь", "Смирнов", "1985-05-30"),
            ("owner6", "Елена", "Волкова", "1991-09-12"),
            ("owner7", "Павел", "Орлов", "1993-12-25"),
        ]
        owners = []
        for username, first_name, last_name, birth in owners_data:
            owner, created = CarOwner.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "birth_date": date.fromisoformat(birth),
                    "passport_number": f"40{username[-1]}0123456",
                    "home_address": f"СПб, ул. Примерная, {username[-1]}",
                    "nationality": "РФ",
                },
            )
            if created:
                owner.set_password("demo-owner-pass")
                owner.save()
            owners.append(owner)
            self.stdout.write(f"владелец: {owner} (id={owner.id})")

        cars_data = [
            ("А111АА178", "Toyota", "Camry", "красный"),
            ("В222ВВ178", "Toyota", "Corolla", "белый"),
            ("С333СС178", "BMW", "X5", "чёрный"),
            ("Е444ЕЕ178", "Lada", "Vesta", "красный"),
            ("К555КК178", "Audi", "A4", "синий"),
            ("М666ММ178", "Toyota", "RAV4", "серый"),
        ]
        cars = []
        for plate, brand, model, color in cars_data:
            car, _ = Car.objects.get_or_create(
                license_plate=plate,
                defaults={"brand": brand, "model": model, "color": color},
            )
            cars.append(car)
            self.stdout.write(f"авто: {car}")

        licenses_data = [
            (0, "AA111111", "B", "2008-04-10"),
            (1, "BB222222", "B", "2012-06-15"),
            (2, "CC333333", "B", "2010-01-20"),
            (3, "DD444444", "B", "2015-09-05"),
            (4, "EE555555", "C", "2005-03-18"),
            (5, "FF666666", "B", "2018-11-22"),
            (6, "GG777777", "B", "2011-07-07"),
        ]
        for idx, number, ltype, issued in licenses_data:
            lic, _ = DriverLicense.objects.get_or_create(
                owner=owners[idx],
                license_number=number,
                defaults={"license_type": ltype, "issue_date": date.fromisoformat(issued)},
            )
            self.stdout.write(f"удостоверение: {lic} -> {owners[idx]}")

        ownerships = [
            (0, 0, "2009-01-01", None),
            (0, 1, "2011-05-01", "2019-01-01"),
            (1, 1, "2019-02-01", None),
            (2, 2, "2010-08-01", None),
            (2, 3, "2013-03-01", None),
            (3, 3, "2016-01-01", None),
            (4, 4, "2006-06-01", None),
            (4, 0, "2014-04-01", "2018-04-01"),
            (4, 5, "2020-01-01", None),
            (5, 5, "2018-12-01", None),
            (6, 2, "2012-02-01", "2015-02-01"),
            (6, 4, "2021-05-01", None),
        ]
        for owner_i, car_i, start, end in ownerships:
            own, _ = Ownership.objects.get_or_create(
                owner=owners[owner_i],
                car=cars[car_i],
                start_date=date.fromisoformat(start),
                defaults={"end_date": date.fromisoformat(end) if end else None},
            )
            self.stdout.write(f"владение: {own}")

        self.stdout.write("\n=== Практическое задание 2: фильтры ===")
        toyota = Car.objects.filter(brand="Toyota")
        self.stdout.write(f"Toyota: {list(toyota)}")

        olegs = CarOwner.objects.filter(first_name="Олег")
        self.stdout.write(f"владельцы с именем Олег: {list(olegs)}")

        random_owner = owners[0]
        self.stdout.write(f"случайный владелец id={random_owner.id}")
        license_obj = DriverLicense.objects.get(owner_id=random_owner.id)
        self.stdout.write(f"удостоверение по id владельца: {license_obj}")

        red_owners = CarOwner.objects.filter(cars__color="красный").distinct()
        self.stdout.write(f"владельцы красных машин: {list(red_owners)}")

        from_2010 = CarOwner.objects.filter(ownerships__start_date__year__gte=2010).distinct()
        self.stdout.write(f"владельцы с владением с 2010: {list(from_2010)}")

        self.stdout.write("\n=== Практическое задание 3: агрегация ===")
        oldest = DriverLicense.objects.aggregate(oldest=Min("issue_date"))
        self.stdout.write(f"самая ранняя дата выдачи удостоверения: {oldest}")

        latest_own = Ownership.objects.filter(car__model__in=Car.objects.values("model")).aggregate(
            latest=Max("start_date")
        )
        self.stdout.write(f"самая поздняя дата владения (по существующим моделям): {latest_own}")

        cars_per_owner = CarOwner.objects.annotate(cars_count=Count("cars")).values(
            "username", "first_name", "last_name", "cars_count"
        )
        self.stdout.write("число машин у каждого водителя:")
        for row in cars_per_owner:
            self.stdout.write(f"  {row}")

        brand_counts = Car.objects.values("brand").annotate(cnt=Count("id")).order_by("brand")
        self.stdout.write("число машин каждой марки:")
        for row in brand_counts:
            self.stdout.write(f"  {row}")

        by_license = (
            CarOwner.objects.filter(licenses__isnull=False)
            .order_by("licenses__issue_date")
            .distinct()
        )
        self.stdout.write("владельцы по дате выдачи удостоверения:")
        for owner in by_license:
            lic = owner.licenses.order_by("issue_date").first()
            self.stdout.write(f"  {owner} — {lic.issue_date if lic else None}")

from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Count, Max, Min
from django.utils import timezone

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership


OWNERS = (
    ("orlov", "Орлов", "Олег", (1987, 4, 12), "P31-000001", (2005, 5, 3)),
    ("sokolova", "Соколова", "Ирина", (1988, 9, 20), "P31-000002", (2012, 9, 18)),
    ("volkov", "Волков", "Дмитрий", (1985, 2, 8), "P31-000003", (2008, 4, 12)),
    ("smirnov", "Смирнов", "Алексей", (1991, 6, 17), "P31-000004", (2010, 1, 25)),
    ("kuznetsova", "Кузнецова", "Анна", (1995, 11, 2), "P31-000005", (2018, 7, 30)),
    ("pavlova", "Павлова", "Мария", (1990, 3, 14), "P31-000006", (2015, 3, 14)),
    ("morozov", "Морозов", "Илья", (1989, 12, 5), "P31-000007", (2009, 11, 2)),
)

CARS = (
    ("corolla", "P31-CAR-001", "Toyota", "Corolla", "красный"),
    ("camry", "P31-CAR-002", "Toyota", "Camry", "чёрный"),
    ("vesta", "P31-CAR-003", "Lada", "Vesta", "красный"),
    ("rio", "P31-CAR-004", "Kia", "Rio", "белый"),
    ("solaris", "P31-CAR-005", "Hyundai", "Solaris", "синий"),
    ("focus", "P31-CAR-006", "Ford", "Focus", "красный"),
)

OWNERSHIPS = (
    ("orlov", "corolla", (2010, 6, 1)),
    ("orlov", "camry", (2012, 3, 1)),
    ("sokolova", "corolla", (2015, 1, 1)),
    ("volkov", "vesta", (2010, 1, 20)),
    ("volkov", "rio", (2016, 2, 11)),
    ("smirnov", "vesta", (2015, 7, 1)),
    ("kuznetsova", "solaris", (2020, 8, 14)),
    ("pavlova", "focus", (2011, 3, 10)),
    ("morozov", "rio", (2019, 1, 1)),
    ("morozov", "focus", (2018, 8, 1)),
)


class Command(BaseCommand):
    help = "3.1"

    def handle(self, *args, **options):
        owners, cars = self.create_practice_data()
        self.print_created_objects(owners)
        self.run_filtering_queries(owners)
        self.run_aggregation_queries()

    @staticmethod
    def make_datetime(parts):
        return timezone.make_aware(datetime(*parts))

    def create_practice_data(self):
        owners = {}
        cars = {}

        for key, last_name, first_name, birth_date, license_number, issue_date in OWNERS:
            owner, _ = CarOwner.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={"birth_date": self.make_datetime(birth_date)},
            )
            owners[key] = owner
            DriverLicense.objects.update_or_create(
                license_number=license_number,
                defaults={
                    "owner": owner,
                    "license_type": "B",
                    "issue_date": self.make_datetime(issue_date),
                },
            )

        for key, registration_number, brand, model, color in CARS:
            car, _ = Car.objects.get_or_create(
                registration_number=registration_number,
                defaults={"brand": brand, "model": model, "color": color},
            )
            cars[key] = car

        for owner_key, car_key, start_date in OWNERSHIPS:
            Ownership.objects.get_or_create(
                owner=owners[owner_key],
                car=cars[car_key],
                start_date=self.make_datetime(start_date),
                defaults={"end_date": None},
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Подготовлены данные: 7 владельцев, 7 удостоверений, "
                "6 автомобилей и 10 записей о владении."
            )
        )
        return owners, cars

    def print_created_objects(self, owners):
        self.stdout.write("\nСозданные владельцы, удостоверения и автомобили:")
        for owner in sorted(owners.values(), key=lambda item: (item.last_name, item.first_name)):
            license_record = owner.licenses.order_by("issue_date").first()
            self.stdout.write(
                "\n{} — удостоверение {} (выдано {}):".format(
                    owner,
                    license_record.license_number if license_record else "нет",
                    self.format_date(license_record.issue_date) if license_record else "нет",
                )
            )
            for ownership in owner.ownership_records.select_related("car").order_by("start_date"):
                self.stdout.write(
                    "  {} {}, цвет {}; владение с {}".format(
                        ownership.car.brand,
                        ownership.car.model,
                        ownership.car.color,
                        self.format_date(ownership.start_date),
                    )
                )

    def run_filtering_queries(self, owners):
        self.stdout.write("\nПрактическое задание 2 — фильтрация:")
        self.print_lines(
            "Все автомобили Toyota:",
            [str(car) for car in Car.objects.filter(brand__iexact="Toyota").order_by("model")],
        )
        self.print_lines(
            "Владельцы с именем Алексей:",
            [
                str(owner)
                for owner in CarOwner.objects.filter(first_name__iexact="Алексей").order_by(
                    "last_name", "first_name"
                )
            ],
        )

        owner_id = owners["orlov"].pk
        owner = CarOwner.objects.get(pk=owner_id)
        license_record = owner.licenses.order_by("issue_date").first()
        self.stdout.write(
            "\nУдостоверение владельца с ID {}: {}".format(
                owner_id, license_record.license_number if license_record else "не найдено"
            )
        )

        self.print_lines(
            "Владельцы красных автомобилей:",
            [
                str(owner)
                for owner in CarOwner.objects.filter(cars__color__iexact="красный")
                .distinct()
                .order_by("last_name", "first_name")
            ],
        )
        self.print_lines(
            "Владельцы, у которых владение автомобилем началось в 2010 году:",
            [
                str(owner)
                for owner in CarOwner.objects.filter(ownership_records__start_date__year=2010)
                .distinct()
                .order_by("last_name", "first_name")
            ],
        )

    def run_aggregation_queries(self):
        self.stdout.write("\nПрактическое задание 3 — агрегация, аннотация и сортировка:")

        oldest_license_date = DriverLicense.objects.aggregate(
            oldest_issue_date=Min("issue_date")
        )["oldest_issue_date"]
        self.stdout.write(
            "\nДата выдачи самого старого удостоверения: {}".format(
                self.format_date(oldest_license_date)
            )
        )

        selected_model = "Vesta"
        latest_ownership_date = Ownership.objects.filter(
            car__model__iexact=selected_model
        ).aggregate(latest_start_date=Max("start_date"))["latest_start_date"]
        self.stdout.write(
            "Самая поздняя дата начала владения автомобилем модели {}: {}".format(
                selected_model, self.format_date(latest_ownership_date)
            )
        )

        self.stdout.write("\nКоличество автомобилей у каждого владельца:")
        owners_with_car_counts = CarOwner.objects.annotate(
            car_count=Count("ownership_records__car", distinct=True)
        ).order_by("last_name", "first_name")
        for owner in owners_with_car_counts:
            self.stdout.write("  {}: {}".format(owner, owner.car_count))

        self.stdout.write("\nКоличество автомобилей каждой марки:")
        brand_counts = Car.objects.values("brand").annotate(car_count=Count("id")).order_by(
            "brand"
        )
        for item in brand_counts:
            self.stdout.write("  {}: {}".format(item["brand"], item["car_count"]))

        self.stdout.write("\nВладельцы по дате выдачи удостоверения:")
        owners_by_license_date = (
            CarOwner.objects.filter(licenses__isnull=False)
            .annotate(first_license_date=Min("licenses__issue_date"))
            .order_by("first_license_date", "last_name", "first_name")
            .distinct()
        )
        for owner in owners_by_license_date:
            self.stdout.write(
                "  {}: {}".format(owner, self.format_date(owner.first_license_date))
            )

    def print_lines(self, title, lines):
        self.stdout.write("\n{}".format(title))
        if not lines:
            self.stdout.write("  Ничего не найдено.")
            return
        for line in lines:
            self.stdout.write("  {}".format(line))

    @staticmethod
    def format_date(value):
        if value is None:
            return "нет данных"
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.strftime("%Y-%m-%d")

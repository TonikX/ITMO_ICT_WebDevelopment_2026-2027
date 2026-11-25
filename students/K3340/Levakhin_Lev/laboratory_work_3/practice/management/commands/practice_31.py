from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Max, Min

from practice.models import Car, License, Owner, Ownership


class Command(BaseCommand):
    help = "Создать демонстрационные данные и выполнить запросы практики 3.1"

    @transaction.atomic
    def handle(self, *args, **options):
        cars = [
            Car.objects.get_or_create(brand=brand, model=model, color=color)[0]
            for brand, model, color in [
                ("Toyota", "Corolla", "красный"), ("Toyota", "Camry", "чёрный"),
                ("Kia", "Rio", "синий"), ("Lada", "Vesta", "красный"),
                ("Ford", "Focus", "белый"), ("Skoda", "Octavia", "чёрный"),
            ]
        ]
        for index, name in enumerate(("Олег", "Анна", "Иван", "Олег", "Мария", "Алексей", "Ольга")):
            owner, _ = Owner.objects.get_or_create(
                passport_number=f"DEMO-{index}", defaults={"first_name": name, "last_name": "Орлов"},
            )
            License.objects.get_or_create(
                owner=owner, defaults={"number": f"DEMO-{index}", "issued_on": date(2008 + index, 4, 15)},
            )
            # through хранит собственное поле с датой начала владения
            for offset in range(index % 3 + 1):
                Ownership.objects.get_or_create(
                    owner=owner, car=cars[(index + offset) % len(cars)], started_on=date(2010 + index, 5, 1),
                )
        owners = Owner.objects.filter(passport_number__startswith="DEMO-")
        sample = owners.first()
        license_record = License.objects.get(owner_id=sample.id)
        results = [
            ("Созданные владельцы и машины", list(owners.values("id", "first_name", "cars__model"))),
            ("Toyota", list(Car.objects.filter(brand="Toyota").values_list("model", flat=True))),
            ("Олеги", list(owners.filter(first_name="Олег").values_list("id", flat=True))),
            ("Удостоверение владельца", (sample.id, license_record.number, license_record.issued_on)),
            ("Владельцы красных авто", list(owners.filter(cars__color="красный").distinct().values_list("id", flat=True))),
            ("Владение с 2010", list(owners.filter(ownerships__started_on__year=2010).distinct().values_list("id", flat=True))),
            ("Самое старое удостоверение", License.objects.aggregate(oldest=Min("issued_on"))),
            ("Последнее начало владения Corolla", Ownership.objects.filter(car__model="Corolla").aggregate(latest=Max("started_on"))),
            ("Машин у владельца", list(owners.annotate(car_count=Count("cars", distinct=True)).values("id", "car_count"))),
            ("Машин каждой марки", list(Car.objects.values("brand").annotate(car_count=Count("id")).order_by("brand"))),
            ("Владельцы по выдаче удостоверения", list(owners.order_by("license__issued_on", "id").distinct().values_list("id", flat=True))),
        ]
        for label, result in results:
            self.stdout.write(f"{label}: {result}")

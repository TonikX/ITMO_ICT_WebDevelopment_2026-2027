from datetime import date

from django.db.models import Count, Max, Min
from django.test import TestCase

from .models import Car, CarOwner, DriverLicense, Ownership


class Practice31OrmTests(TestCase):
    def setUp(self):
        self.owner = CarOwner.objects.create(
            first_name="Олег",
            last_name="Иванов",
            birth_date=date(1985, 1, 1),
        )
        self.other = CarOwner.objects.create(
            first_name="Анна",
            last_name="Петрова",
            birth_date=date(1990, 1, 1),
        )
        self.toyota = Car.objects.create(
            state_number="A1",
            brand="Toyota",
            model="Camry",
            color="красный",
        )
        self.bmw = Car.objects.create(
            state_number="B2",
            brand="BMW",
            model="X5",
            color="белый",
        )
        Ownership.objects.create(
            owner=self.owner,
            car=self.toyota,
            start_date=date(2010, 5, 1),
        )
        Ownership.objects.create(
            owner=self.other,
            car=self.bmw,
            start_date=date(2015, 1, 1),
        )
        DriverLicense.objects.create(
            owner=self.owner,
            license_number="L1",
            license_type="B",
            issue_date=date(2008, 1, 1),
        )
        DriverLicense.objects.create(
            owner=self.other,
            license_number="L2",
            license_type="B",
            issue_date=date(2012, 1, 1),
        )

    def test_filters_and_aggregates(self):
        self.assertEqual(Car.objects.filter(brand="Toyota").count(), 1)
        self.assertEqual(CarOwner.objects.filter(first_name="Олег").count(), 1)
        license_obj = DriverLicense.objects.get(owner_id=self.owner.id)
        self.assertEqual(license_obj.license_number, "L1")
        self.assertEqual(
            CarOwner.objects.filter(cars__color="красный").distinct().count(),
            1,
        )
        self.assertEqual(
            CarOwner.objects.filter(ownerships__start_date__year=2010)
            .distinct()
            .count(),
            1,
        )
        oldest = DriverLicense.objects.aggregate(oldest=Min("issue_date"))
        self.assertEqual(oldest["oldest"], date(2008, 1, 1))
        latest = Ownership.objects.filter(car__model="Camry").aggregate(
            latest=Max("start_date"),
        )
        self.assertEqual(latest["latest"], date(2010, 5, 1))
        annotated = list(
            CarOwner.objects.annotate(cars_count=Count("cars")).order_by("id"),
        )
        self.assertEqual(annotated[0].cars_count, 1)
        brands = list(Car.objects.values("brand").annotate(count=Count("id")))
        self.assertEqual(len(brands), 2)

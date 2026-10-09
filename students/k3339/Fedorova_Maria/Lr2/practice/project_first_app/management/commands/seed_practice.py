from datetime import date

from django.core.management.base import BaseCommand

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership


class Command(BaseCommand):
    help = "Seed demo car owners, cars, ownerships and licenses"

    def handle(self, *args, **options):
        if CarOwner.objects.filter(username="ivanov").exists():
            self.stdout.write("Seed data already exists, skip.")
            return

        owners_data = [
            {
                "username": "ivanov",
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "birth_date": date(1990, 5, 12),
                "passport_number": "4010 111222",
                "home_address": "St. Petersburg, Nevsky 1",
                "nationality": "Russian",
            },
            {
                "username": "petrova",
                "first_name": "Anna",
                "last_name": "Petrova",
                "birth_date": date(1992, 8, 3),
                "passport_number": "4011 333444",
                "home_address": "Moscow, Tverskaya 10",
                "nationality": "Russian",
            },
            {
                "username": "sidorov",
                "first_name": "Petr",
                "last_name": "Sidorov",
                "birth_date": date(1988, 1, 20),
                "passport_number": "4012 555666",
                "home_address": "Kazan, Bauman 5",
                "nationality": "Tatar",
            },
        ]

        owners = []
        for data in owners_data:
            owner = CarOwner.objects.create_user(
                password="secret12",
                **data,
            )
            owners.append(owner)

        cars = [
            Car.objects.create(
                state_number="A123BC178",
                brand="Toyota",
                model="Camry",
                color="Black",
            ),
            Car.objects.create(
                state_number="B456DE178",
                brand="BMW",
                model="X5",
                color="White",
            ),
            Car.objects.create(
                state_number="C789FG178",
                brand="Lada",
                model="Vesta",
                color="Blue",
            ),
            Car.objects.create(
                state_number="E111HH178",
                brand="Kia",
                model="Rio",
                color="Red",
            ),
        ]

        Ownership.objects.create(
            owner=owners[0],
            car=cars[0],
            start_date=date(2018, 1, 1),
            end_date=date(2020, 1, 1),
        )
        Ownership.objects.create(
            owner=owners[0],
            car=cars[1],
            start_date=date(2020, 2, 1),
            end_date=date(2022, 2, 1),
        )
        Ownership.objects.create(
            owner=owners[0],
            car=cars[2],
            start_date=date(2022, 3, 1),
            end_date=None,
        )

        Ownership.objects.create(
            owner=owners[1],
            car=cars[0],
            start_date=date(2020, 2, 1),
            end_date=date(2021, 6, 1),
        )
        Ownership.objects.create(
            owner=owners[1],
            car=cars[2],
            start_date=date(2019, 1, 1),
            end_date=date(2021, 1, 1),
        )
        Ownership.objects.create(
            owner=owners[1],
            car=cars[3],
            start_date=date(2021, 7, 1),
            end_date=None,
        )

        Ownership.objects.create(
            owner=owners[2],
            car=cars[1],
            start_date=date(2017, 5, 1),
            end_date=date(2019, 5, 1),
        )
        Ownership.objects.create(
            owner=owners[2],
            car=cars[3],
            start_date=date(2019, 6, 1),
            end_date=date(2021, 6, 1),
        )
        Ownership.objects.create(
            owner=owners[2],
            car=cars[0],
            start_date=date(2021, 7, 1),
            end_date=None,
        )

        DriverLicense.objects.create(
            owner=owners[0],
            license_number="77AA123456",
            license_type="B",
            issue_date=date(2015, 6, 1),
        )
        DriverLicense.objects.create(
            owner=owners[1],
            license_number="78BB654321",
            license_type="B",
            issue_date=date(2016, 3, 15),
        )
        DriverLicense.objects.create(
            owner=owners[2],
            license_number="16CC111222",
            license_type="C",
            issue_date=date(2014, 9, 20),
        )

        if not CarOwner.objects.filter(username="admin").exists():
            CarOwner.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin",
                first_name="Admin",
                last_name="User",
            )

        self.stdout.write(self.style.SUCCESS("Seed data created."))

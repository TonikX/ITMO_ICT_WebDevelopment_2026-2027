"""Проверки практик: пользователь, FBV, CBV и история владения."""

from datetime import date
from secrets import token_urlsafe

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Car, DriverLicense, Ownership, User


class PracticeTests(TestCase):
    """Проверяет задания 2.1–2.3 через реальные формы."""

    def setUp(self) -> None:
        self.password = token_urlsafe(24)
        self.staff = User.objects.create_user(
            "staff",
            is_staff=True,
            first_name="Иван",
            last_name="Петров",
            birth_date=date(2000, 1, 1),
            passport_number="0000000001",
            address="Учебный адрес",
            nationality="Не указана",
        )
        self.client.force_login(self.staff)

    def test_create_three_owners_with_extended_fields(self) -> None:
        for number in range(3):
            response = self.client.post(
                reverse("practice:owner_create"),
                {
                    "username": f"owner{number}",
                    "first_name": "Иван",
                    "last_name": f"Петров{number}",
                    "password1": self.password,
                    "password2": self.password,
                    "birth_date": "2000-05-01",
                    "passport_number": f"000000000{number}",
                    "address": "Учебный адрес",
                    "nationality": "Не указана",
                    "is_staff": "true",
                },
            )
            self.assertEqual(response.status_code, 302)
            owner = User.objects.get(username=f"owner{number}")
            self.assertFalse(owner.is_staff)
            self.assertEqual(owner.passport_number, f"000000000{number}")
            self.assertContains(
                self.client.get(reverse("practice:owner_detail", args=[owner.pk])),
                owner.passport_number,
            )
        self.assertEqual(User.objects.filter(username__startswith="owner").count(), 3)
        self.assertContains(self.client.get(reverse("practice:owner_list")), "Петров2")

    def test_create_list_detail_edit_delete_three_cars(self) -> None:
        for number in range(3):
            data = {
                "plate_number": f"TEST{number}",
                "brand": "Lada",
                "model_name": "Vesta",
                "color": "Белый",
            }
            self.assertEqual(
                self.client.post(reverse("practice:car_create"), data).status_code, 302
            )
        car = Car.objects.first()
        self.assertContains(self.client.get(reverse("practice:car_list")), "TEST2")
        self.assertContains(
            self.client.get(reverse("practice:car_detail", args=[car.pk])), "Белый"
        )
        data = {
            "plate_number": car.plate_number,
            "brand": "Lada",
            "model_name": "Vesta",
            "color": "Чёрный",
        }
        self.assertEqual(
            self.client.post(
                reverse("practice:car_edit", args=[car.pk]), data
            ).status_code,
            302,
        )
        car.refresh_from_db()
        self.assertEqual(car.color, "Чёрный")
        address = reverse("practice:car_delete", args=[car.pk])
        self.assertEqual(self.client.get(address).status_code, 200)
        self.assertEqual(Car.objects.count(), 3)
        self.assertEqual(self.client.post(address).status_code, 302)
        self.assertEqual(Car.objects.count(), 2)

    def test_m2m_through_and_non_overlapping_ownership(self) -> None:
        car = Car.objects.create(plate_number="A001", brand="Lada", model_name="Vesta")
        other = User.objects.create_user(
            "owner",
            first_name="Анна",
            last_name="Смирнова",
            birth_date=date(2000, 1, 2),
            passport_number="0000000002",
            address="Учебный адрес",
            nationality="Не указана",
        )
        first = Ownership(
            owner=self.staff,
            car=car,
            start_date=date(2020, 1, 1),
            end_date=date(2021, 1, 1),
        )
        first.full_clean()
        first.save()
        second = Ownership(owner=other, car=car, start_date=date(2021, 1, 2))
        second.full_clean()
        second.save()
        self.assertEqual(car.owners.count(), 2)
        overlap = Ownership(owner=other, car=car, start_date=date(2020, 6, 1))
        with self.assertRaises(ValidationError):
            overlap.full_clean()
        first.end_date = date(2019, 1, 1)
        with self.assertRaises(ValidationError):
            first.full_clean()

    def test_driving_license_is_linked_to_owner(self) -> None:
        license = DriverLicense.objects.create(
            owner=self.staff,
            number="1234567890",
            category="B",
            issue_date=date(2020, 1, 1),
        )
        self.assertEqual(license.owner, self.staff)

    def test_private_owner_data_is_staff_only(self) -> None:
        user = User.objects.create_user("ordinary")
        self.client.force_login(user)
        for route, args in [
            ("owner_list", []),
            ("owner_detail", [self.staff.pk]),
            ("owner_create", []),
            ("car_list", []),
            ("car_create", []),
        ]:
            self.assertEqual(
                self.client.get(reverse(f"practice:{route}", args=args)).status_code,
                403,
            )

    def test_admin_displays_extended_fields(self) -> None:
        admin = User.objects.create_superuser("admin", password=token_urlsafe(24))
        self.client.force_login(admin)
        response = self.client.get(
            reverse("admin:project_first_app_user_change", args=[self.staff.pk])
        )
        self.assertContains(response, "passport_number")
        self.assertContains(response, "nationality")

    def test_admin_creates_two_owners_and_four_cars(self) -> None:
        admin = User.objects.create_superuser("admin", password=token_urlsafe(24))
        self.client.force_login(admin)
        owners = []
        for number in range(2):
            response = self.client.post(
                reverse("admin:project_first_app_user_add"),
                {
                    "username": f"admin_owner{number}",
                    "password1": self.password,
                    "password2": self.password,
                    "usable_password": "true",
                    "first_name": "Иван",
                    "last_name": f"Петров{number}",
                    "passport_number": f"000000000{number}",
                    "address": "Учебный адрес",
                    "nationality": "Не указана",
                    "birth_date": "2000-01-01",
                },
            )
            self.assertEqual(response.status_code, 302)
            owners.append(User.objects.get(username=f"admin_owner{number}"))
        cars = []
        for number in range(4):
            response = self.client.post(
                reverse("admin:project_first_app_car_add"),
                {
                    "plate_number": f"ADMIN{number}",
                    "brand": "Lada",
                    "model_name": "Vesta",
                    "color": "Белый",
                },
            )
            self.assertEqual(response.status_code, 302)
            cars.append(Car.objects.get(plate_number=f"ADMIN{number}"))
        for owner, selected, start, end in [
            (owners[0], cars[:3], "2023-01-01", "2024-12-31"),
            (owners[1], cars[1:], "2025-01-01", ""),
        ]:
            for car in selected:
                response = self.client.post(
                    reverse("admin:project_first_app_ownership_add"),
                    {
                        "owner": owner.pk,
                        "car": car.pk,
                        "start_date": start,
                        "end_date": end,
                    },
                )
                self.assertEqual(response.status_code, 302)
        self.assertEqual(Ownership.objects.count(), 6)
        self.assertTrue(all(owner.cars.count() == 3 for owner in owners))

    def test_demo_data_is_repeatable(self) -> None:
        from io import StringIO

        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(Car.objects.count(), 4)
        self.assertEqual(Ownership.objects.count(), 6)
        self.assertFalse(
            User.objects.get(username="demo_owner_1").has_usable_password()
        )

    def test_owner_form_requires_birth_date(self) -> None:
        response = self.client.post(
            reverse("practice:owner_create"),
            {
                "username": "missing_date",
                "password1": self.password,
                "password2": self.password,
                "first_name": "Иван",
                "last_name": "Петров",
                "passport_number": "0000000000",
                "address": "Учебный адрес",
                "nationality": "Не указана",
            },
        )
        self.assertContains(response, "errorlist")
        self.assertFalse(User.objects.filter(username="missing_date").exists())

    def test_owner_birth_date_is_enforced_by_database(self) -> None:
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("missing_date", passport_number="0000000000")

    def test_conference_author_does_not_need_owner_fields(self) -> None:
        author = User(username="author_without_car")
        author.full_clean(exclude=["password"])
        author.save()
        self.assertIsNone(author.birth_date)

    def test_admin_rejects_owner_without_birth_date(self) -> None:
        owner = User(
            username="incomplete_owner",
            first_name="Иван",
            last_name="Петров",
            passport_number="0000000000",
            address="Учебный адрес",
            nationality="Не указана",
        )
        with self.assertRaises(ValidationError) as error:
            owner.full_clean(exclude=["password"])
        self.assertIn("birth_date", error.exception.message_dict)
        admin = User.objects.create_superuser("admin_birth_date")
        self.client.force_login(admin)
        response = self.client.post(
            reverse("admin:project_first_app_user_add"),
            {
                "username": owner.username,
                "password1": self.password,
                "password2": self.password,
                "first_name": owner.first_name,
                "last_name": owner.last_name,
                "passport_number": owner.passport_number,
                "address": owner.address,
                "nationality": owner.nationality,
            },
        )
        self.assertContains(response, "Укажите данные автовладельца.")
        self.assertFalse(User.objects.filter(username=owner.username).exists())


class OwnerIntegrityTests(TestCase):
    """Не допускает обход обязательных данных через связанные admin-формы."""

    def setUp(self) -> None:
        self.admin = User.objects.create_superuser("owner_admin")
        self.author = User.objects.create_user("conference_author")
        self.owner = User.objects.create_user(
            "complete_owner",
            first_name="Иван",
            last_name="Петров",
            birth_date=date(2000, 1, 1),
            passport_number="0000000001",
            address="Учебный адрес",
            nationality="Не указана",
        )
        self.car = Car.objects.create(
            plate_number="OWNER1",
            brand="Lada",
            model_name="Vesta",
        )
        self.client.force_login(self.admin)

    def ownership_data(self, owner: User) -> dict:
        return {"owner": owner.pk, "car": self.car.pk, "start_date": "2025-01-01"}

    def user_data(self) -> dict:
        joined = timezone.localtime(self.owner.date_joined)
        return {
            "username": self.owner.username,
            "first_name": self.owner.first_name,
            "last_name": self.owner.last_name,
            "birth_date": "2000-01-01",
            "passport_number": self.owner.passport_number,
            "address": self.owner.address,
            "nationality": self.owner.nationality,
            "is_active": "on",
            "date_joined_0": joined.strftime("%Y-%m-%d"),
            "date_joined_1": joined.strftime("%H:%M:%S"),
        }

    def test_admin_rejects_ownership_for_incomplete_author(self) -> None:
        response = self.client.post(
            reverse("admin:project_first_app_ownership_add"),
            self.ownership_data(self.author),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("owner", response.context["adminform"].form.errors)
        self.assertFalse(Ownership.objects.exists())

    def test_admin_accepts_complete_owner_and_rejects_reassignment(self) -> None:
        response = self.client.post(
            reverse("admin:project_first_app_ownership_add"),
            self.ownership_data(self.owner),
        )
        self.assertEqual(response.status_code, 302)
        ownership = Ownership.objects.get()
        response = self.client.post(
            reverse("admin:project_first_app_ownership_change", args=[ownership.pk]),
            self.ownership_data(self.author),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("owner", response.context["adminform"].form.errors)
        ownership.refresh_from_db()
        self.assertEqual(ownership.owner, self.owner)

    def test_admin_cannot_clear_required_fields_of_existing_owner(self) -> None:
        Ownership.objects.create(
            owner=self.owner,
            car=self.car,
            start_date=date(2025, 1, 1),
        )
        address = reverse("admin:project_first_app_user_change", args=[self.owner.pk])
        self.assertEqual(self.client.post(address, self.user_data()).status_code, 302)
        required = [
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "address",
            "nationality",
        ]
        for field in required:
            with self.subTest(field=field):
                data = self.user_data()
                data[field] = ""
                response = self.client.post(address, data)
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["adminform"].form.errors)
                self.owner.refresh_from_db()
                self.assertTrue(getattr(self.owner, field))
        data = self.user_data()
        data.update(passport_number="", birth_date="")
        response = self.client.post(address, data)
        self.assertEqual(response.status_code, 200)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.passport_number, "0000000001")
        self.assertEqual(self.owner.birth_date, date(2000, 1, 1))

    def test_whitespace_is_not_valid_owner_information(self) -> None:
        self.owner.passport_number = "   "
        with self.assertRaises(ValidationError):
            self.owner.validate_owner_fields()

    def test_admin_rejects_license_for_incomplete_author(self) -> None:
        response = self.client.post(
            reverse("admin:project_first_app_driverlicense_add"),
            {
                "owner": self.author.pk,
                "number": "0000000001",
                "category": "B",
                "issue_date": "2020-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("owner", response.context["adminform"].form.errors)
        self.assertFalse(DriverLicense.objects.exists())

    def test_user_with_license_cannot_clear_owner_fields(self) -> None:
        DriverLicense.objects.create(
            owner=self.owner,
            number="0000000001",
            category="B",
            issue_date=date(2020, 1, 1),
        )
        self.owner.passport_number = ""
        with self.assertRaises(ValidationError) as error:
            self.owner.full_clean(exclude=["password"])
        self.assertIn("passport_number", error.exception.message_dict)

from datetime import date
from secrets import token_urlsafe
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from .models import Car, DriverLicense, Ownership


class PracticeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser("admin", "", token_urlsafe(32), first_name="Админ", last_name="Тестов",
            passport_number="0000000001", home_address="Учебный адрес", nationality="Русский")
        cls.car = Car.objects.create(registration_number="А001АА178", brand="Toyota", model_name="Corolla")

    def owner_data(self, index):
        password = token_urlsafe(32)
        return {"username": f"test_owner{index}", "password1": password, "password2": password,
                "first_name": "Иван", "last_name": f"Тестов{index}", "birth_date": "1995-02-10",
                "passport_number": f"4000{index:06}", "home_address": "Санкт-Петербург", "nationality": "Русский"}

    def test_owner_creation_via_fbv_stores_user_fields_and_hashed_password(self):
        for i in range(3):
            data = self.owner_data(i)
            response = self.client.post(reverse("owner_create"), data)
            self.assertEqual(response.status_code, 302)
            owner = get_user_model().objects.get(username=f"test_owner{i}")
            self.assertTrue(owner.check_password(data["password1"]))
            self.assertEqual(owner.passport_number, f"4000{i:06}")
            self.assertEqual(owner.home_address, "Санкт-Петербург")
            self.assertFalse(owner.is_staff or owner.is_superuser)
            self.assertContains(self.client.get(reverse("owner", args=[owner.pk])), f"Тестов{i}")
        self.assertContains(self.client.get(reverse("owners")), "test_owner2")
        self.assertEqual(self.client.get("/owner/999999/").status_code, 404)

    def test_car_crud_via_cbv_and_delete_confirmation(self):
        self.assertEqual(self.client.post(reverse("car_create"), {}).status_code, 302)
        self.client.force_login(self.admin)
        for i in range(3):
            data = {"registration_number": f"Т{i:03}ТТ178", "brand": "Kia", "model_name": "Rio", "color": "Белый"}
            self.assertEqual(self.client.post(reverse("car_create"), data).status_code, 302)
        car = Car.objects.get(registration_number="Т000ТТ178")
        self.assertContains(self.client.get(reverse("car", args=[car.pk])), "Kia")
        self.assertContains(self.client.get(reverse("cars")), "Т002ТТ178")
        data["registration_number"] = car.registration_number
        data["color"] = "Синий"
        self.assertEqual(self.client.post(reverse("car_update", args=[car.pk]), data).status_code, 302)
        car.refresh_from_db()
        self.assertEqual(car.color, "Синий")
        url = reverse("car_delete", args=[car.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Car.objects.filter(pk=car.pk).exists())
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertFalse(Car.objects.filter(pk=car.pk).exists())

    def test_all_models_registered_and_admin_can_create_owner(self):
        self.client.force_login(self.admin)
        for model in ["carowner", "car", "ownership", "driverlicense"]:
            self.assertEqual(self.client.get(reverse(f"admin:project_first_app_{model}_changelist")).status_code, 200)
        response = self.client.post(reverse("admin:project_first_app_carowner_add"), self.owner_data(10))
        self.assertEqual(response.status_code, 302)
        owner = get_user_model().objects.get(username="test_owner10")
        response = self.client.get(reverse("admin:project_first_app_carowner_change", args=[owner.pk]))
        for field in ["passport_number", "home_address", "nationality"]:
            self.assertContains(response, f'id="id_{field}"')
        self.assertEqual(self.client.get(f"/owner/{owner.pk}").status_code, 301)

    def test_ownership_intervals_and_m2m(self):
        first = Ownership.objects.create(owner=self.admin, car=self.car, start_date=date(2020,1,1), end_date=date(2021,12,31))
        self.assertIn(self.admin, self.car.owners.all())
        self.assertIn(self.car, self.admin.cars.all())
        for start,end in [(date(2019,1,1),date(2020,1,1)), (date(2021,1,1),None), (date(2021,12,31),date(2022,12,31))]:
            with self.assertRaises(ValidationError):
                Ownership(owner=self.admin, car=self.car, start_date=start, end_date=end).full_clean()
        Ownership(owner=self.admin, car=self.car, start_date=date(2022,1,1)).full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Ownership.objects.create(owner=self.admin, car=self.car, start_date=date(2025,1,1), end_date=date(2024,1,1))
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse("owner", args=[self.admin.pk])), first.car.registration_number)

    def test_demo_minimum_counts_and_non_overlapping_history(self):
        call_command("seed_demo", verbosity=0)
        self.assertEqual(get_user_model().objects.filter(username__startswith="owner").count(), 6)
        self.assertGreaterEqual(Car.objects.count(), 7)
        self.assertEqual(DriverLicense.objects.count(), 2)
        for owner in get_user_model().objects.filter(username__in=["owner1","owner2"]):
            self.assertEqual(owner.cars.distinct().count(), 3)
        for ownership in Ownership.objects.all():
            ownership.full_clean()
        counts = (get_user_model().objects.count(), Car.objects.count(), Ownership.objects.count())
        call_command("seed_demo", verbosity=0)
        self.assertEqual(counts, (get_user_model().objects.count(), Car.objects.count(), Ownership.objects.count()))

    def test_private_owner_fields_visible_only_to_owner_and_staff(self):
        self.client.post(reverse("owner_create"), self.owner_data(20))
        owner = get_user_model().objects.get(username="test_owner20")
        url = reverse("owner", args=[owner.pk])
        self.assertNotContains(self.client.get(url), owner.passport_number)
        self.client.force_login(owner)
        self.assertContains(self.client.get(url), owner.passport_number)
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(url), owner.home_address)

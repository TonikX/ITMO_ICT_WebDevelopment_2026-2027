import secrets
from datetime import date

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Car, CarOwner, Ownership


PASSWORD = secrets.token_urlsafe(16)  # пароли в тестах случайные


class SeedTests(TestCase):
    def test_seed_matches_assignment(self):
        call_command("seed", verbosity=0)
        owners = CarOwner.objects.filter(is_superuser=False)
        self.assertEqual(owners.count(), 2)
        self.assertEqual(Car.objects.count(), 4)
        for owner in owners:
            self.assertGreaterEqual(owner.ownerships.count(), 3)

    def test_first_owner_has_id_1(self):
        call_command("seed", verbosity=0)
        self.assertEqual(CarOwner.objects.get(pk=1).username, "ivanov")

    def test_ownership_dates_do_not_overlap_per_car(self):
        call_command("seed", verbosity=0)
        for car in Car.objects.all():
            periods = sorted(car.ownerships.all(), key=lambda o: o.start_date)
            for prev, nxt in zip(periods, periods[1:]):
                self.assertIsNotNone(prev.end_date)
                self.assertLess(prev.end_date, nxt.start_date)


class ViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)
        cls.owner = CarOwner.objects.get(username="ivanov")

    def test_owner_detail_shows_owner_fields(self):
        r = self.client.get(f"/owner/{self.owner.pk}/")
        self.assertContains(r, "Иванов")
        self.assertContains(r, "4510 123456")  # поля из практики 2.3
        self.assertEqual(self.client.get("/owner/9999/").status_code, 404)

    def test_owner_list_and_car_views(self):
        self.assertContains(self.client.get("/owners/"), "Петров")
        self.assertContains(self.client.get("/cars/"), "А001АА77")
        self.assertNotContains(self.client.get("/cars/", {"brand": "kia"}), "Toyota")
        car = Car.objects.get(state_number="С333СС99")
        self.assertContains(self.client.get(f"/cars/{car.pk}/"), "Kia")

    def test_create_owner_via_form(self):
        r = self.client.post(
            "/owners/new/",
            {
                "username": "sidorov", "first_name": "Сидор", "last_name": "Сидоров", "birth_date": "1995-05-05",
                "passport_number": "1111 222222", "home_address": "Казань", "nationality": "татарин",
                "password1": PASSWORD, "password2": PASSWORD,
            },
        )
        new = CarOwner.objects.get(username="sidorov")
        self.assertRedirects(r, f"/owner/{new.pk}/")
        self.assertEqual(new.passport_number, "1111 222222")
        self.assertTrue(new.check_password(PASSWORD))

    def test_car_crud(self):
        self.client.post("/cars/create/", {"state_number": "Н555НН", "brand": "Audi", "model": "A4", "color": "красный"})
        car = Car.objects.get(state_number="Н555НН")
        self.client.post(f"/cars/{car.pk}/update/", {"state_number": "Н555НН", "brand": "Audi", "model": "A6", "color": ""})
        car.refresh_from_db()
        self.assertEqual(car.model, "A6")
        self.client.post(f"/cars/{car.pk}/delete/")
        self.assertFalse(Car.objects.filter(pk=car.pk).exists())

    def test_deleting_car_cascades_ownerships(self):
        car = Car.objects.get(state_number="А001АА77")
        car.delete()
        self.assertFalse(Ownership.objects.filter(car_id=car.pk).exists())

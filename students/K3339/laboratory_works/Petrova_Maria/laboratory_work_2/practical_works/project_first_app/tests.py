from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Car, CarOwner, Ownership


class PracticalWorkTests(TestCase):
    fixtures = ["sample_data"]

    def test_owner_page(self):
        response = self.client.get("/owner/1/")
        self.assertContains(response, "Иванов")
        self.assertContains(response, "Toyota")
        self.assertContains(response, "7810123456")

    def test_missing_owner(self):
        response = self.client.get("/owner/999/")
        self.assertEqual(response.status_code, 404)

    def test_url_without_slash(self):
        self.assertRedirects(self.client.get("/owner/1"), "/owner/1/", status_code=301)

    def test_sample_data(self):
        self.assertEqual(CarOwner.objects.count(), 2)
        self.assertEqual(Car.objects.count(), 4)
        for owner in CarOwner.objects.all():
            self.assertEqual(owner.cars.distinct().count(), 3)
        for car in Car.objects.all():
            periods = list(Ownership.objects.filter(car=car).order_by("start_date"))
            for previous, current in zip(periods, periods[1:]):
                self.assertIsNotNone(previous.end_date)
                self.assertLess(previous.end_date, current.start_date)


class FormTests(TestCase):
    fixtures = ["sample_data"]

    def test_lists_and_forms(self):
        for url in ["/", "/owners/", "/owners/create/", "/cars/", "/cars/create/",
                    "/cars/1/", "/cars/1/update/", "/cars/1/delete/"]:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(self.client.get("/owners/"), "Иванов")
        self.assertContains(self.client.get("/cars/"), "Toyota")

    def test_owner_create(self):
        response = self.client.post("/owners/create/", {
            "last_name": "Сидоров", "first_name": "Петр",
            "birth_date": "1992-03-12T00:00",
            "username": "petr", "passport_number": "0000123456",
            "home_address": "Учебный адрес, 1", "nationality": "Русский",
            "password1": "Study-password-2026!", "password2": "Study-password-2026!",
        })
        owner = CarOwner.objects.get(last_name="Сидоров")
        self.assertRedirects(response, f"/owner/{owner.id}/")
        self.assertEqual(owner.birth_date.year, 1992)
        self.assertEqual(owner.passport_number, "0000123456")
        self.assertEqual(owner.home_address, "Учебный адрес, 1")
        self.assertEqual(owner.nationality, "Русский")
        self.assertTrue(owner.check_password("Study-password-2026!"))
        self.assertFalse(owner.is_staff)
        self.assertTrue(self.client.login(username="petr", password="Study-password-2026!"))
        self.assertContains(self.client.get(f"/owner/{owner.id}/"), "0000123456")

    def test_invalid_forms(self):
        for url in ["/owners/create/", "/cars/create/", "/cars/1/update/"]:
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertEqual(CarOwner.objects.count(), 2)
        self.assertEqual(Car.objects.count(), 4)
        self.assertEqual(Car.objects.get(pk=1).brand, "Toyota")

    def test_car_create_update_delete(self):
        data = {"license_plate": "А111АА178", "brand": "Ford",
                "model": "Focus", "color": "Белый"}
        self.assertRedirects(self.client.post("/cars/create/", data), "/cars/")
        car = Car.objects.get(license_plate="А111АА178")
        data["color"] = "Черный"
        self.assertRedirects(self.client.post(f"/cars/{car.id}/update/", data), "/cars/")
        car.refresh_from_db()
        self.assertEqual(car.color, "Черный")
        self.assertEqual(self.client.get(f"/cars/{car.id}/delete/").status_code, 200)
        self.assertTrue(Car.objects.filter(pk=car.id).exists())
        self.assertRedirects(self.client.post(f"/cars/{car.id}/delete/"), "/cars/")
        self.assertFalse(Car.objects.filter(pk=car.id).exists())

    def test_missing_car(self):
        for url in ["/cars/999/", "/cars/999/update/", "/cars/999/delete/"]:
            self.assertEqual(self.client.get(url).status_code, 404)


class UserTests(TestCase):
    def test_registration_validation(self):
        data = {
            "username": "student", "first_name": "Иван", "last_name": "Сидоров",
            "passport_number": "0000123456", "home_address": "Учебный адрес, 1",
            "nationality": "Русский", "password1": "Study-password-2026!",
            "password2": "different-password",
        }
        response = self.client.post("/owners/create/", data)
        self.assertIn("password2", response.context["form"].errors)
        self.assertEqual(get_user_model().objects.count(), 0)
        data["password2"] = data["password1"]
        data["passport_number"] = ""
        response = self.client.post("/owners/create/", data)
        self.assertIn("passport_number", response.context["form"].errors)
        data["passport_number"] = "0000123456"
        self.assertEqual(self.client.post("/owners/create/", data).status_code, 302)
        response = self.client.post("/owners/create/", data)
        self.assertIn("username", response.context["form"].errors)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_user_admin(self):
        user = get_user_model().objects.create_superuser(
            username="admin", password="Admin-test-password!",
        )
        self.client.force_login(user)
        for url in [
            "/admin/project_first_app/carowner/add/",
            f"/admin/project_first_app/carowner/{user.pk}/change/",
        ]:
            response = self.client.get(url)
            for field in ["passport_number", "home_address", "nationality"]:
                self.assertContains(response, f'name="{field}"')

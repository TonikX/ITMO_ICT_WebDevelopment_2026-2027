from datetime import date

from django.test import Client, TestCase
from django.urls import reverse

from .models import Car, CarOwner, Ownership


class PracticeViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = CarOwner.objects.create_user(
            username="tester",
            password="secret12",
            first_name="Test",
            last_name="User",
            birth_date=date(1995, 1, 1),
            passport_number="0000 111111",
            home_address="Test street",
            nationality="Russian",
        )
        self.car = Car.objects.create(
            state_number="T001TT178",
            brand="Ford",
            model="Focus",
            color="Gray",
        )
        Ownership.objects.create(
            owner=self.owner,
            car=self.car,
            start_date=date(2020, 1, 1),
        )

    def test_owner_detail(self):
        response = self.client.get(
            reverse("owner_detail", args=[self.owner.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")
        self.assertContains(response, "0000 111111")

    def test_owner_list_and_car_list(self):
        owners = self.client.get(reverse("owner_list"))
        cars = self.client.get(reverse("car_list"))
        self.assertEqual(owners.status_code, 200)
        self.assertEqual(cars.status_code, 200)
        self.assertContains(cars, "Ford")

    def test_car_create_requires_staff(self):
        guest = self.client.post(
            reverse("car_create"),
            {
                "state_number": "X999XX178",
                "brand": "Audi",
                "model": "A4",
                "color": "Silver",
            },
        )
        self.assertEqual(guest.status_code, 302)
        self.assertFalse(Car.objects.filter(state_number="X999XX178").exists())

        staff = CarOwner.objects.create_superuser(
            username="boss",
            email="boss@example.com",
            password="secret12",
        )
        self.client.force_login(staff)
        response = self.client.post(
            reverse("car_create"),
            {
                "state_number": "X999XX178",
                "brand": "Audi",
                "model": "A4",
                "color": "Silver",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Car.objects.filter(state_number="X999XX178").exists())

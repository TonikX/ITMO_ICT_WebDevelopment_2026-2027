from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Agency, Country, Reservation, Tour


class TourApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.country = Country.objects.create(name="Italy")
        self.agency = Agency.objects.create(name="Sun Travel")
        self.tour = Tour.objects.create(
            name="Rome weekend",
            agency=self.agency,
            country=self.country,
            description="Short city break",
            start_date="2026-05-01",
            end_date="2026-05-05",
            payment_terms="50% deposit",
            price="45000.00",
        )
        self.user = User.objects.create_user(
            username="client",
            password="secret12",
        )
        self.staff = User.objects.create_user(
            username="admin",
            password="secret12",
            is_staff=True,
        )

    def test_register_and_list_tours(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "newbie",
                "email": "n@example.com",
                "password": "secret12",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        tours_response = self.client.get("/api/tours/")
        self.assertEqual(tours_response.status_code, status.HTTP_200_OK)
        self.assertIn("results", tours_response.data)
        self.assertEqual(tours_response.data["count"], 1)

    def test_reservation_confirm_and_sold_table(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        book = self.client.post(
            "/api/reservations/",
            {"tour": self.tour.id},
            format="json",
        )
        self.assertEqual(book.status_code, status.HTTP_201_CREATED)
        reservation_id = book.data["id"]
        self.assertFalse(book.data["is_confirmed"])

        staff_token = Token.objects.create(user=self.staff)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {staff_token.key}")

        confirm = self.client.patch(
            f"/api/admin/reservations/{reservation_id}/confirm/",
        )
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        self.assertTrue(confirm.data["is_confirmed"])

        sold = self.client.get("/api/admin/stats/sold-by-country/")
        self.assertEqual(sold.status_code, status.HTTP_200_OK)
        self.assertEqual(len(sold.data), 1)
        self.assertEqual(sold.data[0]["country"], "Italy")
        self.assertEqual(sold.data[0]["tour"], "Rome weekend")

        reservation = Reservation.objects.get(pk=reservation_id)
        self.assertTrue(reservation.is_confirmed)

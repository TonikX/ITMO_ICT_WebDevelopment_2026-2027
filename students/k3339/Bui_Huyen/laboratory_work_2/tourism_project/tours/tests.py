from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Country, TourCompany, Tour, Booking, Review

User = get_user_model()
TEST_PASSWORD = "test-password-placeholder"

class NordwayTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD,
        )

        cls.staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password=TEST_PASSWORD,
            is_staff=True,
        )

        cls.country = Country.objects.create(
            name="Italy",
            description="Test country",
        )

        cls.company = TourCompany.objects.create(
            name="Nordway Travel",
            email="travel@example.com",
        )

        cls.tour = Tour.objects.create(
            title="Rome Tour",
            country=cls.country,
            company=cls.company,
            description="A test tour in Rome.",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=35),
            price=Decimal("500.00"),
            available_places=10,
            is_active=True,
        )

    def test_home_page_returns_success(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rome Tour")

    def test_inactive_tour_is_not_displayed(self):
        self.tour.is_active = False
        self.tour.save()

        response = self.client.get(reverse("home"))

        self.assertNotContains(response, "Rome Tour")

    def test_user_can_register(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": TEST_PASSWORD,
                "password2": TEST_PASSWORD,
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(
            User.objects.filter(username="newuser").exists()
        )

    def test_anonymous_user_cannot_open_my_bookings(self):
        response = self.client.get(reverse("my_bookings"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_user_can_create_booking(self):
        self.client.login(
            username="testuser",
            password=TEST_PASSWORD,
        )

        response = self.client.post(
            reverse("create_booking", args=[self.tour.pk]),
            {"people_count": 3},
        )

        self.assertRedirects(
            response,
            reverse("my_bookings"),
        )

        booking = Booking.objects.get(
            user=self.user,
            tour=self.tour,
        )

        self.assertEqual(booking.people_count, 3)
        self.assertEqual(
            booking.status,
            Booking.Status.PENDING,
        )

        self.tour.refresh_from_db()
        self.assertEqual(self.tour.available_places, 7)

    def test_booking_is_rejected_when_places_are_insufficient(self):
        self.client.login(
            username="testuser",
            password=TEST_PASSWORD,
        )

        response = self.client.post(
            reverse("create_booking", args=[self.tour.pk]),
            {"people_count": 11},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Booking.objects.filter(
                user=self.user,
                tour=self.tour,
            ).exists()
        )

        self.tour.refresh_from_db()
        self.assertEqual(self.tour.available_places, 10)

    def test_user_can_cancel_pending_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            tour=self.tour,
            people_count=2,
            status=Booking.Status.PENDING,
        )

        self.client.login(
            username="testuser",
            password=TEST_PASSWORD,
        )

        response = self.client.post(
            reverse("cancel_booking", args=[booking.pk])
        )

        self.assertRedirects(
            response,
            reverse("my_bookings"),
        )

        booking.refresh_from_db()
        self.tour.refresh_from_db()

        self.assertEqual(
            booking.status,
            Booking.Status.CANCELLED,
        )
        self.assertEqual(self.tour.available_places, 12)

    def test_user_can_add_review(self):
        self.client.login(
            username="testuser",
            password=TEST_PASSWORD,
        )

        response = self.client.post(
            reverse("create_review", args=[self.tour.pk]),
            {
                "content": "Excellent tour!",
                "score": 9,
            },
        )

        self.assertRedirects(
            response,
            reverse("tour_detail", args=[self.tour.pk]),
        )

        self.assertTrue(
            Review.objects.filter(
                user=self.user,
                tour=self.tour,
                score=9,
            ).exists()
        )

    def test_staff_can_open_country_statistics(self):
        self.client.login(
            username="staffuser",
            password=TEST_PASSWORD,
        )

        response = self.client.get(
            reverse("country_statistics")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Italy")

    def test_regular_user_cannot_open_country_statistics(self):
        self.client.login(
            username="testuser",
            password=TEST_PASSWORD,
        )

        response = self.client.get(
            reverse("country_statistics")
        )

        self.assertEqual(response.status_code, 302)
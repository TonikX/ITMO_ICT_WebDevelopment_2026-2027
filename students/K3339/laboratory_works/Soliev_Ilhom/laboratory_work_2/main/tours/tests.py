from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Agency, Booking, Country, Review, Tour


class TourSiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("traveler", password="Travel-password-42")
        cls.other = User.objects.create_user("other", password="Travel-password-42")
        cls.manager = User.objects.create_user("manager", password="Travel-password-42", is_staff=True)
        cls.country = Country.objects.create(name="Грузия")
        cls.agency = Agency.objects.create(name="В путь", phone="1234567", email="info@example.com")
        cls.tour = Tour.objects.create(
            title="Тбилиси", country=cls.country, agency=cls.agency, description="Поездка в Тбилиси",
            start_date=timezone.localdate() + timedelta(days=30),
            end_date=timezone.localdate() + timedelta(days=35),
            payment_terms="Предоплата 30%", price=Decimal("50000"),
        )

    def make_booking(self, **kwargs):
        data = {"user": self.user, "tour": self.tour, "unit_price": self.tour.price,
                "travelers": 2, "phone": "+7 900 123-45-67"}
        data.update(kwargs)
        return Booking.objects.create(**data)

    def test_public_pages_and_login_render(self):
        for name, args in [("tour_list", []), ("tour_detail", [self.tour.pk]),
                           ("sales", []), ("login", []), ("register", [])]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200)

    def test_registration_and_login(self):
        response = self.client.post(reverse("register"), {
            "username": "new_traveler", "email": "new@example.com", "first_name": "Иван",
            "last_name": "Петров", "password1": "New-travel-password-42", "password2": "New-travel-password-42",
        })
        self.assertRedirects(response, reverse("tour_list"))
        self.assertTrue(User.objects.get(username="new_traveler").check_password("New-travel-password-42"))
        self.assertIn("_auth_user_id", self.client.session)
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post(reverse("login"), {"username": "new_traveler", "password": "New-travel-password-42"})
        self.assertRedirects(response, reverse("tour_list"))

    def test_booking_requires_login(self):
        response = self.client.post(reverse("booking_create", args=[self.tour.pk]), {"travelers": 1, "phone": "123"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.count(), 0)

    def test_booking_cannot_spoof_owner_status_or_price(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("booking_create", args=[self.tour.pk]), {
            "travelers": 3, "phone": "123456789", "comment": "Рядом с морем",
            "status": "confirmed", "user": self.other.pk, "unit_price": "1",
        })
        self.assertRedirects(response, reverse("my_bookings"))
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertEqual(booking.total_price, Decimal("150000"))
        self.client.post(reverse("booking_create", args=[self.tour.pk]), {"travelers": 2, "phone": "123"})
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_edit_resets_confirmation_and_preserves_price(self):
        booking = self.make_booking(status=Booking.Status.CONFIRMED)
        self.tour.price = 70000
        self.tour.save()
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("booking_edit", args=[booking.pk])).status_code, 200)
        response = self.client.post(reverse("booking_edit", args=[booking.pk]), {"travelers": 3, "phone": "987654321"})
        self.assertRedirects(response, reverse("my_bookings"))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertEqual(booking.total_price, Decimal("150000"))

    def test_user_cannot_edit_or_delete_another_booking(self):
        booking = self.make_booking(user=self.other)
        self.client.force_login(self.user)
        for name in ["booking_edit", "booking_delete"]:
            self.assertEqual(self.client.post(reverse(name, args=[booking.pk]), {"travelers": 1, "phone": "123"}).status_code, 404)
        self.assertNotContains(self.client.get(reverse("my_bookings")), self.tour.title)
        self.assertTrue(Booking.objects.filter(pk=booking.pk).exists())

    def test_delete_requires_post(self):
        booking = self.make_booking()
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("booking_delete", args=[booking.pk])).status_code, 200)
        self.assertTrue(Booking.objects.filter(pk=booking.pk).exists())
        self.assertRedirects(self.client.post(reverse("booking_delete", args=[booking.pk])), reverse("my_bookings"))
        self.assertFalse(Booking.objects.exists())

    def test_invalid_traveler_count_and_past_tour(self):
        self.client.force_login(self.user)
        for travelers in [0, 21]:
            response = self.client.post(reverse("booking_create", args=[self.tour.pk]), {"travelers": travelers, "phone": "123"})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "errorlist")
        self.tour.start_date = timezone.localdate() - timedelta(days=1)
        self.tour.save()
        response = self.client.post(reverse("booking_create", args=[self.tour.pk]), {"travelers": 1, "phone": "123"})
        self.assertContains(response, "Этот тур уже начался")
        self.assertFalse(Booking.objects.exists())

    def test_review_validation_author_dates_and_escaping(self):
        endpoint = reverse("review_create", args=[self.tour.pk])
        self.assertEqual(self.client.post(endpoint, {"rating": 5, "text": "Хорошо"}).status_code, 302)
        self.client.force_login(self.user)
        for rating in [0, 11]:
            self.assertEqual(self.client.post(endpoint, {"rating": rating, "text": "Отзыв"}).status_code, 200)
        self.assertFalse(Review.objects.exists())
        response = self.client.post(endpoint, {
            "rating": 9, "text": "<script>alert(1)</script>",
            "user": self.other.pk, "start_date": "2000-01-01",
        })
        self.assertRedirects(response, reverse("tour_detail", args=[self.tour.pk]))
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.start_date, self.tour.start_date)
        self.assertEqual(review.end_date, self.tour.end_date)
        page = self.client.get(reverse("tour_detail", args=[self.tour.pk]))
        self.assertContains(page, "&lt;script&gt;")
        self.assertNotContains(page, "<script>")

    def test_manager_permissions_and_confirmation(self):
        booking = self.make_booking()
        endpoint = reverse("booking_confirm", args=[booking.pk])
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get(reverse("tour_list")), "Управление заявками")
        self.assertEqual(self.client.get(reverse("booking_manage")).status_code, 302)
        self.assertEqual(self.client.post(endpoint).status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.client.force_login(self.manager)
        self.assertContains(self.client.get(reverse("booking_manage")), "Подтвердить")
        self.assertEqual(self.client.get(endpoint).status_code, 405)
        self.assertRedirects(self.client.post(endpoint), reverse("booking_manage"))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)

    def test_admin_can_confirm_booking(self):
        self.manager.is_superuser = True
        self.manager.save()
        booking = self.make_booking()
        self.client.force_login(self.manager)
        endpoint = reverse("admin:tours_booking_changelist")
        self.assertEqual(self.client.get(endpoint).status_code, 200)
        response = self.client.post(endpoint, {"action": "confirm_bookings", "_selected_action": booking.pk})
        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)

    def test_sales_only_count_confirmed_bookings(self):
        self.make_booking(status=Booking.Status.CONFIRMED)
        self.make_booking(user=self.other, travelers=5)
        response = self.client.get(reverse("sales"))
        self.assertInHTML(
            "<tr><td>Грузия</td><td>1</td><td>2</td><td>100\u00a0000 ₽</td></tr>",
            response.content.decode(),
        )
        self.assertContains(response, self.tour.title)
        self.assertNotContains(response, "250\u00a0000")

    def test_search_filter_and_pagination(self):
        for index in range(7):
            tour = Tour.objects.get(pk=self.tour.pk)
            tour.pk = None
            tour.title = f"Маршрут {index}"
            tour.save()
        response = self.client.get(reverse("tour_list"), {"country": self.country.pk, "page": 2})
        self.assertContains(response, "Страница 2 из 2")
        self.assertContains(response, 'class="panel tour-card"', count=2)
        self.assertContains(response, f"country={self.country.pk}")
        response = self.client.get(reverse("tour_list"), {"q": "Маршрут 6", "country": self.country.pk})
        self.assertContains(response, 'class="panel tour-card"', count=1)
        self.assertContains(response, "Маршрут 6")
        country = Country.objects.create(name="Армения")
        response = self.client.get(reverse("tour_list"), {"country": country.pk})
        self.assertContains(response, "Туры не найдены")
        response = self.client.get(reverse("tour_list"), {"q": "Не найдено"})
        self.assertContains(response, "Туры не найдены")

    def test_dates_and_csrf_validation(self):
        self.tour.end_date = self.tour.start_date - timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.tour.full_clean()
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.manager)
        booking = self.make_booking()
        self.assertEqual(csrf_client.post(reverse("booking_confirm", args=[booking.pk])).status_code, 403)

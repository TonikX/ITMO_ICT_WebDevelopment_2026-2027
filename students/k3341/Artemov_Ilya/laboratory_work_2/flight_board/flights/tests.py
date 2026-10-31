from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from secrets import token_urlsafe
from threading import Barrier

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, close_old_connections, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from .models import Flight, Reservation, Review


def make_flight(**values):
    departure = timezone.now().replace(second=0, microsecond=0) + timedelta(days=2)
    data = dict(number="SU100", airline="Аэрофлот", origin="Санкт-Петербург",
                destination="Москва", departure_at=departure, arrival_at=departure + timedelta(hours=2),
                direction="departure", gate="A1", seat_count=5)
    data.update(values)
    return Flight.objects.create(**data)


class FlightBoardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user("traveler", password=token_urlsafe(32), first_name="Иван", last_name="Иванов")
        cls.other = User.objects.create_user("other", password=token_urlsafe(32))
        cls.staff = User.objects.create_superuser("dispatcher", "", token_urlsafe(32))
        cls.flight = make_flight()
        cls.reservation = Reservation.objects.create(user=cls.user, flight=cls.flight, passenger_name="Иван Иванов", seat_number=1)

    def test_jinja_pages_and_role_controls(self):
        for url in ["/", reverse("flights:detail", args=[self.flight.pk]), "/accounts/login/", "/accounts/signup/"]:
            self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.get("/")
        self.assertNotContains(response, "Добавить рейс")
        self.client.force_login(self.staff)
        self.assertContains(self.client.get("/"), "Добавить рейс")
        detail = reverse("flights:detail", args=[self.flight.pk])
        self.assertContains(self.client.get(detail), "Зарегистрировать пассажира")
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get(detail), "Зарегистрировать пассажира")

    def test_signup_cannot_assign_admin_rights(self):
        password = token_urlsafe(32)
        response = self.client.post(reverse("signup"), {
            "username": "new_user", "first_name": "Анна", "last_name": "Тестова", "email": "a@example.com",
            "password1": password, "password2": password, "is_staff": "on", "is_superuser": "on",
        })
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="new_user")
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff or user.is_superuser)

    def test_guest_cannot_modify_data_or_view_passengers(self):
        urls = [reverse("flights:reserve", args=[self.flight.pk]), reverse("flights:passengers", args=[self.flight.pk]),
                reverse("flights:review_create", args=[self.flight.pk]), reverse("flights:my_reservations")]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_booking_checks_seat_capacity_and_ignores_privileged_fields(self):
        self.client.force_login(self.other)
        url = reverse("flights:reserve", args=[self.flight.pk])
        for seat in [0, -1, 1, 6]:
            response = self.client.post(url, {"flight": self.flight.pk, "passenger_name": "Другой пассажир", "seat_number": seat})
            self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 1)
        response = self.client.post(url, {"flight": self.flight.pk, "passenger_name": "Другой пассажир", "seat_number": 2,
                                          "user": self.user.pk, "checked_in": "on", "ticket_number": "FAKE"})
        self.assertEqual(response.status_code, 302)
        reservation = Reservation.objects.get(seat_number=2)
        self.assertEqual(reservation.user, self.other)
        self.assertFalse(reservation.checked_in)
        self.assertIsNone(reservation.ticket_number)

    def test_only_owner_can_edit_or_delete_and_delete_requires_post(self):
        edit = reverse("flights:reservation_update", args=[self.reservation.pk])
        delete = reverse("flights:reservation_delete", args=[self.reservation.pk])
        self.client.force_login(self.other)
        for url in [edit, delete]:
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {}).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(delete).status_code, 200)
        self.assertTrue(Reservation.objects.filter(pk=self.reservation.pk).exists())
        self.assertEqual(self.client.post(delete).status_code, 302)
        self.assertFalse(Reservation.objects.filter(pk=self.reservation.pk).exists())

    def test_booking_can_change_flight_and_reset_checkin(self):
        other_flight = make_flight(number="SU101")
        self.reservation.checked_in = True
        self.reservation.ticket_number = "TICKET-01"
        self.reservation.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse("flights:reservation_update", args=[self.reservation.pk]), {
            "flight": other_flight.pk, "passenger_name": "Иван Иванов", "seat_number": 3,
        })
        self.assertEqual(response.status_code, 302)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.flight, other_flight)
        self.assertEqual(self.reservation.seat_number, 3)
        self.assertFalse(self.reservation.checked_in)
        self.assertIsNone(self.reservation.ticket_number)

    def test_checkin_rights_ticket_and_passenger_table(self):
        url = reverse("flights:check_in", args=[self.reservation.pk])
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(url, {"ticket_number": "T-100"}).status_code, 403)
        table = reverse("flights:passengers", args=[self.flight.pk])
        self.assertContains(self.client.get(table), "Иван Иванов")
        self.assertNotContains(self.client.get(table), "Номер билета")
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(url, {"ticket_number": " "}).status_code, 200)
        self.assertEqual(self.client.post(url, {"ticket_number": "T-100"}).status_code, 302)
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.checked_in)
        self.assertEqual(self.reservation.ticket_number, "T-100")
        self.assertContains(self.client.get(table), "T-100")

    def test_staff_can_register_new_passenger_and_duplicate_ticket_is_rejected(self):
        self.client.force_login(self.staff)
        url = reverse("flights:staff_reserve", args=[self.flight.pk])
        response = self.client.post(url, {"user": self.other.pk, "passenger_name": "Другой пассажир", "seat_number": 2, "ticket_number": "T-200"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reservation.objects.get(seat_number=2).checked_in)
        check_in = reverse("flights:check_in", args=[self.reservation.pk])
        self.assertEqual(self.client.post(check_in, {"ticket_number": "T-200"}).status_code, 200)
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.checked_in)

    def test_admin_can_checkin_passenger_and_reject_invalid_booking(self):
        self.client.force_login(self.staff)
        url = reverse("admin:flights_reservation_change", args=[self.reservation.pk])
        data = {"user": self.user.pk, "flight": self.flight.pk, "passenger_name": "Иван Иванов", "seat_number": 1, "checked_in": "on", "ticket_number": ""}
        self.assertEqual(self.client.post(url, data).status_code, 200)
        data["ticket_number"] = "ADMIN-T100"
        self.assertEqual(self.client.post(url, data).status_code, 302)
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.checked_in)
        self.assertEqual(self.reservation.ticket_number, "ADMIN-T100")
        data["seat_number"] = 6
        self.assertEqual(self.client.post(url, data).status_code, 200)

    def test_review_rating_author_date_and_html_escaping(self):
        self.client.force_login(self.user)
        url = reverse("flights:review_create", args=[self.flight.pk])
        for rating in [0, 11, -1]:
            self.assertEqual(self.client.post(url, {"text": "Проверка", "rating": rating}).status_code, 200)
        self.assertFalse(Review.objects.exists())
        self.assertEqual(self.client.post(url, {"text": "<script>alert(1)</script>", "rating": 10, "user": self.other.pk, "flight_date": "2000-01-01"}).status_code, 302)
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.flight_date, timezone.localdate(self.flight.departure_at))
        response = self.client.get(reverse("flights:detail", args=[self.flight.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert")

    def test_search_filters_pagination_and_invalid_parameters(self):
        for i in range(10):
            make_flight(number=f"SU{200+i}", departure_at=self.flight.departure_at + timedelta(minutes=i+1))
        response = self.client.get("/", {"q": "аэрофлот", "direction": "departure"})
        self.assertContains(response, "Найдено рейсов: 11")
        self.assertContains(response, "page=2")
        self.assertContains(response, "direction=departure")
        self.assertNotContains(response, "SU209")
        self.assertContains(self.client.get("/", {"q": "SU209"}), "Найдено рейсов: 1")
        for params in [{"date": "bad"}, {"direction": "bad"}, {"q": "несуществующий"}]:
            self.assertContains(self.client.get("/", params), "Найдено рейсов: 0")
        for page in ["bad", "-1", "999"]:
            self.assertEqual(self.client.get("/", {"page": page}).status_code, 200)
        date = timezone.localdate(self.flight.departure_at).isoformat()
        self.assertContains(self.client.get("/", {"date": date}), "Найдено рейсов: 11")

    def test_csrf_and_post_only_logout(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        url = reverse("flights:reserve", args=[self.flight.pk])
        self.assertEqual(client.post(url, {"flight": self.flight.pk, "passenger_name": "Тест", "seat_number": 2}).status_code, 403)
        self.assertEqual(client.get(reverse("logout")).status_code, 405)
        self.assertEqual(client.get(url).status_code, 200)
        token = client.cookies["flights_csrftoken"].value
        self.assertEqual(client.post(url, {"csrfmiddlewaretoken": token, "flight": self.flight.pk, "passenger_name": "Тест", "seat_number": 2}).status_code, 302)

    def test_database_constraints_and_capacity_reduction(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Reservation.objects.create(user=self.other, flight=self.flight, passenger_name="Тест", seat_number=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Reservation.objects.create(user=self.other, flight=self.flight, passenger_name="Тест", seat_number=2, checked_in=True)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(user=self.user, flight=self.flight, flight_date=timezone.localdate(), text="Тест", rating=11)
        Reservation.objects.create(user=self.other, flight=self.flight, passenger_name="Тест", seat_number=5)
        self.flight.seat_count = 4
        with self.assertRaises(ValidationError):
            self.flight.full_clean()


class ConcurrentBookingTests(TransactionTestCase):
    def test_two_users_cannot_book_the_same_seat_simultaneously(self):
        flight = make_flight()
        users = [get_user_model().objects.create_user(f"concurrent{i}") for i in range(2)]
        barrier = Barrier(2)

        def reserve(user_id):
            close_old_connections()
            try:
                client = Client()
                client.force_login(get_user_model().objects.get(pk=user_id))
                barrier.wait(timeout=10)
                response = client.post(reverse("flights:reserve", args=[flight.pk]), {
                    "flight": flight.pk, "passenger_name": "Тест", "seat_number": 1,
                })
                return response.status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(executor.map(reserve, [u.pk for u in users]))
        self.assertEqual(sorted(responses), [200, 302])
        self.assertEqual(Reservation.objects.filter(flight=flight, seat_number=1).count(), 1)

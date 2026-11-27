import os
from datetime import date
from html import escape
from io import StringIO
from secrets import token_urlsafe
from unittest.mock import patch
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.forms import modelform_factory
from django.template.loader import get_template
from django.test import Client, TestCase
from django.urls import reverse

from .models import Reservation, Review, Tour


User = get_user_model()
PASSWORD = token_urlsafe(24)


def create_tour(**overrides):
    fields = {
        "name": "Римские каникулы",
        "agency": "Лаборатория путешествий",
        "country": "Италия",
        "description": "Экскурсии по Риму",
        "start_date": date(2026, 6, 1),
        "end_date": date(2026, 6, 7),
        "payment_terms": "Предоплата 30%",
        "price": 75000,
    }
    return Tour.objects.create(**(fields | overrides))


class CatalogTests(TestCase):
    def test_empty_catalog_and_no_search_results(self):
        url = reverse("tour_list")
        self.assertContains(self.client.get(url), "Туры пока не добавлены")
        create_tour()
        response = self.client.get(url, {"q": "нет такого тура", "page": 2})
        self.assertContains(response, "По заданным параметрам туры не найдены")
        self.assertNotContains(response, "<table>")
        self.assertNotContains(response, "Страница 1 из 1")

    def test_search_and_country_filter_survive_pagination(self):
        for number in range(1, 7):
            create_tour(name=f"Маршрут {number}", agency="Рим & Море + 100%")
        create_tour(name="Тур по Франции", agency="Рим & Море + 100%", country="Франция")
        create_tour(name="Другой маршрут")

        url = reverse("tour_list")
        filters = {"q": "рим & море + 100%", "country": "Италия"}
        response = self.client.get(url, filters)
        self.assertContains(response, "Страница 1 из 2")
        self.assertContains(response, "Маршрут 5")
        self.assertNotContains(response, "Маршрут 6")
        self.assertNotContains(response, "Тур по Франции")
        self.assertNotContains(response, "Другой маршрут")

        page_two = urlencode({**filters, "page": 2})
        self.assertContains(response, f'href="?{escape(page_two)}"')
        response = self.client.get(f"{url}?{page_two}")
        self.assertContains(response, "Страница 2 из 2")
        self.assertContains(response, "Маршрут 6")
        self.assertNotContains(response, "Маршрут 5")
        self.assertContains(response, f'href="?{escape(urlencode({**filters, "page": 1}))}"')

    def test_search_by_name_and_country_and_tour_details(self):
        tour = create_tour(description="<b>Индивидуальная экскурсия</b>")
        for query in ("римские", "италия"):
            response = self.client.get(reverse("tour_list"), {"q": query})
            self.assertContains(response, tour.name)

        response = self.client.get(reverse("tour_detail", args=[tour.pk]))
        self.assertContains(response, tour.payment_terms)
        self.assertContains(response, "&lt;b&gt;Индивидуальная экскурсия&lt;/b&gt;")
        self.assertContains(response, "Отзывов пока нет")
        self.assertEqual(self.client.get(reverse("tour_detail", args=[tour.pk + 1])).status_code, 404)

    def test_template_engines(self):
        self.assertEqual(get_template("library/tour_list.html").backend.name, "jinja2")
        self.assertEqual(get_template("admin/login.html").backend.name, "django")


class AccountTests(TestCase):
    def test_registration_logout_and_login_with_csrf(self):
        client = Client(enforce_csrf_checks=True)
        registration = reverse("register")
        logout = reverse("logout")
        login = reverse("login")
        form = {"username": "traveler", "password1": PASSWORD, "password2": PASSWORD}

        self.assertContains(client.get(registration), 'name="csrfmiddlewaretoken"')
        self.assertEqual(client.post(registration, form).status_code, 403)
        form["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
        self.assertRedirects(client.post(registration, form), reverse("tour_list"))
        user = User.objects.get(username="traveler")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(int(client.session["_auth_user_id"]), user.pk)

        self.assertEqual(client.get(logout).status_code, 405)
        self.assertEqual(client.post(logout).status_code, 403)
        csrf_token = client.cookies["csrftoken"].value
        self.assertRedirects(client.post(logout, {"csrfmiddlewaretoken": csrf_token}), reverse("tour_list"))
        self.assertNotIn("_auth_user_id", client.session)

        target = reverse("my_reservations")
        login_url = f"{login}?next={target}"
        self.assertRedirects(client.get(target), login_url)
        self.assertContains(client.get(login_url), f'name="next" value="{target}"')
        credentials = {
            "username": user.username,
            "password": PASSWORD,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        }
        self.assertEqual(
            client.post(login, {**credentials, "password": token_urlsafe(24)}).status_code, 200
        )
        self.assertNotIn("_auth_user_id", client.session)
        self.assertRedirects(client.post(login, {**credentials, "next": target}), target)


class ReservationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tour = create_tour()
        cls.owner = User.objects.create_user("owner")
        cls.other = User.objects.create_user("other")

    def test_customer_creates_edits_and_deletes_own_reservation(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        reserve = reverse("reserve_tour", args=[self.tour.pk])
        self.assertContains(client.get(reserve), 'name="csrfmiddlewaretoken"')
        self.assertEqual(client.post(reserve, {"tourists_count": 2}).status_code, 403)
        csrf_token = client.cookies["csrftoken"].value
        reservations = reverse("my_reservations")
        data = {"tourists_count": 2, "comment": "Два места", "csrfmiddlewaretoken": csrf_token}
        self.assertRedirects(client.post(reserve, data), reservations)
        reservation = Reservation.objects.get(user=self.owner, tour=self.tour)
        self.assertEqual(reservation.tourists_count, 2)
        self.assertFalse(reservation.is_confirmed)
        self.assertContains(client.get(reservations), self.tour.name)

        Reservation.objects.filter(pk=reservation.pk).update(is_confirmed=True)
        edit = reverse("edit_reservation", args=[reservation.pk])
        self.assertContains(client.get(edit), "Два места")
        data = {**data, "tourists_count": 3, "comment": "Три места"}
        self.assertRedirects(client.post(edit, data), reservations)
        reservation.refresh_from_db()
        self.assertEqual(reservation.tourists_count, 3)
        self.assertFalse(reservation.is_confirmed)

        delete = reverse("delete_reservation", args=[reservation.pk])
        self.assertContains(client.get(delete), self.tour.name)
        self.assertEqual(client.post(delete).status_code, 403)
        self.assertRedirects(client.post(delete, {"csrfmiddlewaretoken": csrf_token}), reservations)
        self.assertFalse(Reservation.objects.filter(pk=reservation.pk).exists())

    def test_other_user_cannot_edit_or_delete_reservation(self):
        reservation = Reservation.objects.create(user=self.owner, tour=self.tour)
        self.client.force_login(self.other)
        for name in ("edit_reservation", "delete_reservation"):
            url = reverse(name, args=[reservation.pk])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {"tourists_count": 10}).status_code, 404)
        reservation.refresh_from_db()
        self.assertEqual(reservation.tourists_count, 1)
        self.assertNotContains(self.client.get(reverse("my_reservations")), self.tour.name)

    def test_tourist_count_and_review_rating_validation(self):
        self.client.force_login(self.owner)
        reserve = reverse("reserve_tour", args=[self.tour.pk])
        for value in (-1, 0, "1.5", 2_147_483_648, 10**30):
            self.assertContains(self.client.post(reserve, {"tourists_count": value}), "errorlist")
        self.assertFalse(Reservation.objects.exists())

        add_review = reverse("add_review", args=[self.tour.pk])
        for rating in (0, 11):
            self.assertContains(self.client.post(add_review, {"text": "Отзыв", "rating": rating}), "errorlist")
        self.assertFalse(Review.objects.exists())

        detail = reverse("tour_detail", args=[self.tour.pk])
        self.assertRedirects(self.client.post(add_review, {"text": "Отличный тур", "rating": 10}), detail)
        review = Review.objects.get(user=self.owner, tour=self.tour)
        self.assertEqual((review.tour_start_date, review.tour_end_date), (self.tour.start_date, self.tour.end_date))
        self.assertContains(self.client.get(detail), "рейтинг 10/10")


class AdministrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tour = create_tour()
        cls.customer = User.objects.create_user("customer")
        cls.reservation = Reservation.objects.create(user=cls.customer, tour=cls.tour, tourists_count=2)
        cls.admin = User.objects.create_superuser("admin", password=PASSWORD)

    def test_staff_confirms_on_website_with_post_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        admin_page = reverse("admin_reservations")
        confirm = reverse("confirm_reservation", args=[self.reservation.pk])
        self.assertRedirects(client.get(admin_page), f"{reverse('login')}?next={admin_page}")

        client.force_login(self.customer)
        self.assertRedirects(client.get(admin_page), reverse("tour_list"))
        client.get(reverse("tour_list"))
        csrf_token = client.cookies["csrftoken"].value
        self.assertRedirects(client.post(confirm, {"csrfmiddlewaretoken": csrf_token}), reverse("tour_list"))
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.is_confirmed)

        staff = User.objects.create_user("staff", is_staff=True)
        client.force_login(staff)
        self.assertContains(client.get(admin_page), f'action="{confirm}"')
        self.assertEqual(client.get(confirm).status_code, 405)
        self.assertEqual(client.post(confirm).status_code, 403)
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.is_confirmed)
        csrf_token = client.cookies["csrftoken"].value
        self.assertRedirects(client.post(confirm, {"csrfmiddlewaretoken": csrf_token}), admin_page)
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.is_confirmed)

    def test_django_admin_confirms_reservation_with_change_permission(self):
        admin_page = reverse("admin:library_reservation_changelist")
        action = {"action": "confirm_reservations", "_selected_action": self.reservation.pk, "index": 0}
        viewer = User.objects.create_user("viewer", is_staff=True)
        viewer.user_permissions.add(Permission.objects.get(codename="view_reservation"))
        self.client.force_login(viewer)
        self.assertNotContains(self.client.get(admin_page), 'value="confirm_reservations"')
        self.client.post(admin_page, action)
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.is_confirmed)

        self.client.force_login(self.admin)
        self.assertContains(self.client.get(admin_page), 'value="confirm_reservations"')
        self.assertRedirects(self.client.post(admin_page, action), admin_page)
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.is_confirmed)

    def test_country_report_only_includes_confirmed_sales(self):
        url = reverse("sold_by_country")
        self.assertContains(self.client.get(url), "Подтверждённых бронирований пока нет")
        second_tour = create_tour(name="Сады Тосканы")
        pending_tour = create_tour(name="Париж", country="Франция")
        for tour, count, confirmed in (
            (self.tour, 3, True),
            (self.tour, 5, True),
            (second_tour, 2, True),
            (pending_tour, 20, False),
        ):
            Reservation.objects.create(
                tour=tour, user=self.customer, tourists_count=count, is_confirmed=confirmed
            )
        self.assertContains(
            self.client.get(url),
            "<tr><td>Италия</td><td>Римские каникулы, Сады Тосканы</td><td>3</td><td>10</td></tr>",
            html=True,
        )
        self.assertNotContains(self.client.get(url), pending_tour.country)


class DataTests(TestCase):
    def test_tour_form_validates_price_and_dates(self):
        form_class = modelform_factory(Tour, fields="__all__")
        data = {
            "name": "Тур",
            "agency": "Агентство",
            "country": "Италия",
            "description": "Описание",
            "payment_terms": "Предоплата",
            "start_date": "2026-06-01",
            "end_date": "2026-06-01",
            "price": "0.01",
        }
        self.assertTrue(form_class(data).is_valid())
        for price in ("0", "-1", "0.001"):
            self.assertIn("price", form_class({**data, "price": price}).errors)
        for end_date in ("2026-05-31", "2026-06-31"):
            self.assertIn("end_date", form_class({**data, "end_date": end_date}).errors)

    def test_database_constraints(self):
        tour = create_tour()
        user = User.objects.create_user("traveler")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Tour.objects.filter(pk=tour.pk).update(price=0)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Tour.objects.filter(pk=tour.pk).update(end_date=date(2026, 5, 31))
        with self.assertRaises(IntegrityError), transaction.atomic():
            Reservation.objects.create(tour=tour, user=user, tourists_count=0)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(
                tour=tour, user=user, tour_start_date=tour.start_date,
                tour_end_date=tour.end_date, rating=11, text="Отзыв"
            )

    def test_seed_data_is_idempotent(self):
        with patch.dict(os.environ, {"DEMO_PASSWORD": PASSWORD}):
            call_command("seed_data", stdout=StringIO())
        reservation = Reservation.objects.filter(is_confirmed=False).first()
        reservation.is_confirmed = True
        reservation.save(update_fields=["is_confirmed"])
        with patch.dict(os.environ):
            os.environ.pop("DEMO_PASSWORD", None)
            call_command("seed_data", stdout=StringIO())

        self.assertEqual(Tour.objects.count(), 12)
        self.assertEqual(Tour.objects.values("country").distinct().count(), 12)
        self.assertEqual(User.objects.count(), 3)
        self.assertTrue(User.objects.get(username="tour_demo_anna").check_password(PASSWORD))
        self.assertEqual(Reservation.objects.count(), 12)
        self.assertTrue(Reservation.objects.filter(is_confirmed=False).exists())
        self.assertTrue(Reservation.objects.filter(pk=reservation.pk, is_confirmed=True).exists())
        self.assertEqual(Review.objects.count(), 12)
        self.assertEqual(set(Review.objects.values_list("rating", flat=True)), set(range(1, 11)))

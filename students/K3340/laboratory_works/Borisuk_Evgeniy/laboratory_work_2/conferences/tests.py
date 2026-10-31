"""Проверки варианта №5 на PostgreSQL."""

from datetime import date
from secrets import token_urlsafe

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse

from .models import Conference, Registration, Review, Topic


class ConferenceTests(TestCase):
    """Сценарии гостя, автора и администратора."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.password = token_urlsafe(24)
        cls.user = get_user_model().objects.create_user("author", password=cls.password)
        cls.other = get_user_model().objects.create_user("other")
        cls.staff = get_user_model().objects.create_user("editor", is_staff=True)
        cls.topic = Topic.objects.create(name="Информатика")
        cls.conference = Conference.objects.create(
            title="Наука и технологии",
            location="Санкт-Петербург",
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 12),
            description="Исследования",
            venue_description="Университет",
            participation_terms="Доклад",
        )
        cls.conference.topics.add(cls.topic)

    def register(self) -> Registration:
        return Registration.objects.create(
            conference=self.conference,
            author=self.user,
            presentation_title="Сети",
            abstract="Исследование сетей",
        )

    def test_guest_sees_catalog_and_detail(self) -> None:
        for name, args in [
            ("conference_list", []),
            ("conference_detail", [self.conference.pk]),
        ]:
            response = self.client.get(reverse(name, args=args))
            self.assertContains(response, self.conference.title)
            self.assertNotContains(response, "Участники</a>")

    def test_signup_does_not_accept_staff_flag(self) -> None:
        response = self.client.post(
            reverse("signup"),
            {
                "username": "new_author",
                "password1": self.password,
                "password2": self.password,
                "is_staff": "true",
                "is_superuser": "true",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="new_author")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(self.password))

    def test_login_and_logout(self) -> None:
        self.assertEqual(
            self.client.post(
                reverse("login"), {"username": "author", "password": self.password}
            ).status_code,
            302,
        )
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_empty_signup_returns_errors(self) -> None:
        self.assertEqual(self.client.post(reverse("signup"), {}).status_code, 200)
        self.assertEqual(get_user_model().objects.count(), 3)

    def test_guest_cannot_register_or_review(self) -> None:
        for route in ["registration_create", "review_create"]:
            self.assertEqual(
                self.client.post(
                    reverse(route, args=[self.conference.pk]), {}
                ).status_code,
                302,
            )
        self.assertFalse(Registration.objects.exists())
        self.assertFalse(Review.objects.exists())

    def test_registration_assigns_current_author_and_pending_result(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("registration_create", args=[self.conference.pk]),
            {
                "presentation_title": "Сети",
                "abstract": "Аннотация",
                "author": self.other.pk,
                "result": "recommended",
            },
        )
        self.assertEqual(response.status_code, 302)
        registration = Registration.objects.get()
        self.assertEqual(registration.author, self.user)
        self.assertEqual(registration.result, "pending")

    def test_duplicate_registration_rejected(self) -> None:
        self.register()
        self.client.force_login(self.user)
        self.client.post(
            reverse("registration_create", args=[self.conference.pk]),
            {"presentation_title": "Другое", "abstract": "Текст"},
        )
        self.assertEqual(Registration.objects.count(), 1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.register()

    def test_author_edits_own_registration_and_resets_result(self) -> None:
        registration = self.register()
        registration.result = "recommended"
        registration.save()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("registration_edit", args=[registration.pk]),
            {
                "presentation_title": "Новая тема",
                "abstract": "Новая аннотация",
                "result": "recommended",
            },
        )
        self.assertEqual(response.status_code, 302)
        registration.refresh_from_db()
        self.assertEqual(registration.presentation_title, "Новая тема")
        self.assertEqual(registration.result, "pending")

    def test_unchanged_registration_retains_result(self) -> None:
        registration = self.register()
        registration.result = "recommended"
        registration.save()
        self.client.force_login(self.user)
        self.client.post(
            reverse("registration_edit", args=[registration.pk]),
            {
                "presentation_title": registration.presentation_title,
                "abstract": registration.abstract,
            },
        )
        registration.refresh_from_db()
        self.assertEqual(registration.result, "recommended")

    def test_other_user_cannot_edit_or_delete_registration(self) -> None:
        registration = self.register()
        self.client.force_login(self.other)
        for route in ["registration_edit", "registration_delete"]:
            self.assertEqual(
                self.client.post(
                    reverse(route, args=[registration.pk]), {}
                ).status_code,
                404,
            )
        self.assertTrue(Registration.objects.filter(pk=registration.pk).exists())

    def test_delete_requires_post(self) -> None:
        registration = self.register()
        self.client.force_login(self.user)
        address = reverse("registration_delete", args=[registration.pk])
        self.assertEqual(self.client.get(address).status_code, 200)
        self.assertTrue(Registration.objects.exists())
        self.assertEqual(self.client.post(address).status_code, 302)
        self.assertFalse(Registration.objects.exists())

    def test_invalid_registration_returns_field_errors(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("registration_create", args=[self.conference.pk]),
            {"presentation_title": " ", "abstract": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")
        self.assertFalse(Registration.objects.exists())

    def test_review_saves_author_and_dates(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("review_create", args=[self.conference.pk]),
            {
                "text": "Полезная конференция",
                "rating": 10,
                "author": self.other.pk,
                "start_date": "1999-01-01",
            },
        )
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get()
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.start_date, self.conference.start_date)
        self.assertEqual(review.end_date, self.conference.end_date)

    def test_rating_outside_range_rejected(self) -> None:
        self.client.force_login(self.user)
        for rating in [0, 11, -1, "abc"]:
            with self.subTest(rating=rating):
                response = self.client.post(
                    reverse("review_create", args=[self.conference.pk]),
                    {"text": "Отзыв", "rating": rating},
                )
                self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.exists())

    def test_database_enforces_rating_range(self) -> None:
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(
                conference=self.conference,
                author=self.user,
                start_date=self.conference.start_date,
                end_date=self.conference.end_date,
                rating=11,
                text="Ошибка",
            )

    def test_reviews_escape_user_html(self) -> None:
        Review.objects.create(
            conference=self.conference,
            author=self.user,
            start_date=self.conference.start_date,
            end_date=self.conference.end_date,
            rating=1,
            text="<script>alert(1)</script>",
        )
        response = self.client.get(
            reverse("conference_detail", args=[self.conference.pk])
        )
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_staff_only_participants_and_result_edit(self) -> None:
        registration = self.register()
        for user in [self.user, self.other]:
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse("participants")).status_code, 403)
            self.assertEqual(
                self.client.post(
                    reverse("result_edit", args=[registration.pk]),
                    {"result": "recommended"},
                ).status_code,
                403,
            )
        registration.refresh_from_db()
        self.assertEqual(registration.result, "pending")
        self.client.force_login(self.staff)
        self.assertContains(
            self.client.get(reverse("participants")), registration.presentation_title
        )
        self.assertEqual(
            self.client.post(
                reverse("result_edit", args=[registration.pk]),
                {"result": "recommended"},
            ).status_code,
            302,
        )
        registration.refresh_from_db()
        self.assertEqual(registration.result, "recommended")

    def test_staff_navigation_is_visible(self) -> None:
        self.client.force_login(self.staff)
        self.assertContains(
            self.client.get(reverse("conference_list")), "Участники</a>"
        )

    def test_invalid_result_rejected(self) -> None:
        registration = self.register()
        self.client.force_login(self.staff)
        self.assertEqual(
            self.client.post(
                reverse("result_edit", args=[registration.pk]), {"result": "unknown"}
            ).status_code,
            200,
        )
        registration.refresh_from_db()
        self.assertEqual(registration.result, "pending")

    def test_admin_can_update_result(self) -> None:
        registration = self.register()
        superuser = get_user_model().objects.create_superuser(
            "admin", password=token_urlsafe(24)
        )
        self.client.force_login(superuser)
        response = self.client.post(
            reverse("admin:conferences_registration_change", args=[registration.pk]),
            {
                "conference": self.conference.pk,
                "author": self.user.pk,
                "presentation_title": "Сети",
                "abstract": "Аннотация",
                "result": "recommended",
            },
        )
        self.assertEqual(response.status_code, 302)
        registration.refresh_from_db()
        self.assertEqual(registration.result, "recommended")

    def test_search_filter_and_pagination_keep_parameters(self) -> None:
        for number in range(8):
            conference = Conference.objects.create(
                title=f"Сети {number}",
                location="Москва",
                start_date=date(2026, 12, 1),
                end_date=date(2026, 12, 2),
                description="Сети",
                venue_description="Зал",
                participation_terms="Доклад",
            )
            conference.topics.add(self.topic)
        address = reverse("conference_list")
        response = self.client.get(address, {"q": "Сети", "topic": self.topic.pk})
        self.assertContains(response, "Страница 1 из 2")
        self.assertContains(response, "topic=")
        self.assertNotContains(response, "Наука и технологии")
        response = self.client.get(
            address, {"q": "Сети", "topic": self.topic.pk, "page": 2}
        )
        self.assertContains(response, "Страница 2 из 2")
        self.assertContains(response, "Сети 7")
        self.assertContains(
            self.client.get(address, {"q": "Нет такого"}), "Конференции не найдены"
        )

    def test_invalid_page_and_missing_record(self) -> None:
        self.assertEqual(
            self.client.get(
                reverse("conference_list"), {"page": "invalid", "topic": "bad"}
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("conference_detail", args=[999999])).status_code,
            404,
        )

    def test_invalid_filter_ids_do_not_raise_errors(self) -> None:
        registration = self.register()
        self.client.force_login(self.staff)
        invalid_values = [
            "9" * 5000,
            "9223372036854775808",
            "-1",
            "0",
            "１２",
            "1.5",
            "abc",
        ]
        for value in invalid_values:
            with self.subTest(value=value[:30]):
                catalog = self.client.get(reverse("conference_list"), {"topic": value})
                self.assertContains(catalog, self.conference.title)
                table = self.client.get(reverse("participants"), {"conference": value})
                self.assertContains(table, registration.presentation_title)

    def test_bigint_boundary_filter_ids_are_accepted(self) -> None:
        self.client.force_login(self.staff)
        maximum = "9223372036854775807"
        self.assertContains(
            self.client.get(reverse("conference_list"), {"topic": maximum}),
            "Конференции не найдены",
        )
        self.assertContains(
            self.client.get(reverse("participants"), {"conference": maximum}),
            "Участников пока нет",
        )

    def test_conference_rejects_reversed_dates(self) -> None:
        self.conference.end_date = date(2026, 11, 1)
        with self.assertRaises(ValidationError):
            self.conference.full_clean()

    def test_csrf_required_for_writes(self) -> None:
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(
            client.post(
                reverse("registration_create", args=[self.conference.pk]),
                {"presentation_title": "Сети", "abstract": "Текст"},
            ).status_code,
            403,
        )
        response = client.get(reverse("registration_create", args=[self.conference.pk]))
        self.assertContains(response, "csrfmiddlewaretoken")
        token = client.cookies["csrftoken"].value
        self.assertEqual(
            client.post(
                reverse("registration_create", args=[self.conference.pk]),
                {
                    "presentation_title": "Сети",
                    "abstract": "Текст",
                    "csrfmiddlewaretoken": token,
                },
            ).status_code,
            302,
        )

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Conference, ConferenceReview, Location, TalkSubmission, Theme


class RegistrationViewTests(TestCase):
    def test_registration_page_is_displayed(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Зарегистрироваться")

    def test_valid_registration_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "conference_author",
                "password1": "Strong-test-password-739!",
                "password2": "Strong-test-password-739!",
            },
        )

        self.assertRedirects(response, reverse("conference_list"))
        user = get_user_model().objects.get(username="conference_author")
        self.assertTrue(user.check_password("Strong-test-password-739!"))

    def test_invalid_registration_does_not_create_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "conference_author",
                "password1": "Strong-test-password-739!",
                "password2": "Different-password-739!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(username="conference_author").exists()
        )


class AuthenticationViewTests(TestCase):
    def setUp(self):
        self.password = "Strong-test-password-739!"
        self.user = get_user_model().objects.create_user(
            username="conference_author",
            password=self.password,
        )

    def test_login_page_is_displayed(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Войти")

    def test_valid_credentials_log_user_in(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("register"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_credentials_do_not_log_user_in(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_ends_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ConferenceDetailViewTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Университет",
            address="Санкт-Петербург",
            description="Главный корпус",
        )
        self.theme = Theme.objects.create(
            name="Информационные технологии",
            description="Исследования в области ИТ",
        )
        self.conference = Conference.objects.create(
            name="SciConf 2026",
            description="Научная конференция о современных исследованиях.",
            location=self.location,
            start_date="2026-11-10",
            end_date="2026-11-12",
            participation_terms="Подать тезисы до 1 ноября",
        )
        self.conference.themes.add(self.theme)

    def test_existing_conference_is_displayed(self):
        response = self.client.get(
            reverse("conference_detail", args=[self.conference.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conference.name)
        self.assertContains(response, self.conference.description)
        self.assertContains(response, self.location.name)
        self.assertContains(response, self.theme.name)
        self.assertContains(response, self.conference.participation_terms)

    def test_missing_conference_returns_404(self):
        response = self.client.get(reverse("conference_detail", args=[99999]))

        self.assertEqual(response.status_code, 404)

    def test_only_recommended_submissions_are_displayed(self):
        author = get_user_model().objects.create_user(
            username="talk_author",
            password="Strong-test-password-739!",
        )
        TalkSubmission.objects.create(
            title="Рекомендованный доклад",
            abstract="Аннотация рекомендованного доклада.",
            conference=self.conference,
            author=author,
            recommended_to_publish=True,
        )
        TalkSubmission.objects.create(
            title="Ожидающий решения доклад",
            abstract="Этот доклад ещё не рассмотрен.",
            conference=self.conference,
            author=author,
            recommended_to_publish=None,
        )

        response = self.client.get(
            reverse("conference_detail", args=[self.conference.pk])
        )

        self.assertContains(response, "Рекомендованный доклад")
        self.assertContains(response, "talk_author")
        self.assertNotContains(response, "Ожидающий решения доклад")

    def test_anonymous_user_is_redirected_to_login_to_post_review(self):
        response = self.client.post(
            reverse("conference_detail", args=[self.conference.pk]),
            {"review_text": "Отличная конференция", "rating": 9},
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('conference_detail', args=[self.conference.pk])}",
        )
        self.assertFalse(ConferenceReview.objects.exists())

    def test_authenticated_user_can_post_review(self):
        reviewer = get_user_model().objects.create_user(
            username="conference_reviewer",
            password="Strong-test-password-739!",
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("conference_detail", args=[self.conference.pk]),
            {"review_text": "Хорошая программа и организация.", "rating": 9},
        )

        self.assertRedirects(
            response,
            reverse("conference_detail", args=[self.conference.pk]),
        )
        review = ConferenceReview.objects.get()
        self.assertEqual(review.conference, self.conference)
        self.assertEqual(review.reviewer, reviewer)
        self.assertEqual(review.rating, 9)

    def test_rating_out_of_range_does_not_create_review(self):
        reviewer = get_user_model().objects.create_user(
            username="conference_reviewer",
            password="Strong-test-password-739!",
        )
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse("conference_detail", args=[self.conference.pk]),
            {"review_text": "Текст отзыва", "rating": 11},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ConferenceReview.objects.exists())

    def test_existing_reviews_are_displayed(self):
        reviewer = get_user_model().objects.create_user(
            username="conference_reviewer",
            password="Strong-test-password-739!",
        )
        ConferenceReview.objects.create(
            conference=self.conference,
            reviewer=reviewer,
            review_text="Полезное мероприятие.",
            rating=8,
        )
        self.client.force_login(reviewer)

        response = self.client.get(
            reverse("conference_detail", args=[self.conference.pk])
        )

        self.assertContains(response, "Полезное мероприятие.")
        self.assertContains(response, "conference_reviewer")


class ConferenceListViewTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            name="Главный корпус",
            address="Санкт-Петербург",
            description="Университет",
        )
        self.other_location = Location.objects.create(
            name="Онлайн",
            address="Интернет",
            description="Удалённый формат",
        )
        self.theme = Theme.objects.create(
            name="Информационные технологии",
            description="ИТ",
        )
        self.other_theme = Theme.objects.create(
            name="Математика",
            description="Математические науки",
        )
        for index in range(7):
            conference = Conference.objects.create(
                name=f"SciConf {index}",
                location=self.location if index < 6 else self.other_location,
                start_date=f"2026-11-{10 + index:02d}",
                end_date=f"2026-11-{10 + index:02d}",
                participation_terms="Регистрация открыта",
            )
            conference.themes.add(
                self.theme if index < 6 else self.other_theme
            )

    def test_conference_list_is_paginated(self):
        response = self.client.get(reverse("conference_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 6)
        self.assertEqual(response.context["page_obj"].paginator.count, 7)
        self.assertContains(response, "Научные конференции")

    def test_filters_by_name_theme_and_location(self):
        response = self.client.get(
            reverse("conference_list"),
            {
                "q": "SciConf 6",
                "theme": self.other_theme.pk,
                "location": self.other_location.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertContains(response, "SciConf 6")
        self.assertNotContains(response, "SciConf 0")

    def test_pagination_preserves_active_filters(self):
        response = self.client.get(
            reverse("conference_list"),
            {"q": "SciConf", "page": 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertContains(response, "q=SciConf&amp;page=1")

    def test_invalid_page_number_falls_back_to_last_page(self):
        response = self.client.get(reverse("conference_list"), {"page": "invalid"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 1)

    def test_header_links_logo_home_and_shows_login_for_anonymous_user(self):
        response = self.client.get(reverse("conference_list"))

        self.assertContains(
            response,
            f'href="{reverse("conference_list")}" aria-label="SciConf — главная"',
        )
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, "Войти")
        self.assertNotContains(response, "Выйти")

    def test_header_shows_logout_for_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username="header_user",
            password="Strong-test-password-739!",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("conference_list"))

        self.assertContains(response, "header_user")
        self.assertContains(response, "Выйти")
        self.assertNotContains(response, "Войти")
        self.assertContains(response, f'action="{reverse("logout")}"')


class DemoDataCommandTests(TestCase):
    def test_command_creates_descriptive_conferences_and_is_idempotent(self):
        call_command("seed_demo_data", stdout=StringIO())

        self.assertEqual(Conference.objects.count(), 7)
        self.assertEqual(Location.objects.count(), 4)
        self.assertEqual(Theme.objects.count(), 5)
        conference = Conference.objects.get(
            name="SciConf: Искусственный интеллект 2027"
        )
        self.assertTrue(conference.description)
        self.assertTrue(conference.themes.exists())
        self.assertTrue(all(theme.description for theme in Theme.objects.all()))

        call_command("seed_demo_data", stdout=StringIO())

        self.assertEqual(Conference.objects.count(), 7)
        self.assertEqual(Location.objects.count(), 4)
        self.assertEqual(Theme.objects.count(), 5)


class TalkSubmissionViewTests(TestCase):
    def setUp(self):
        location = Location.objects.create(
            name="Университет",
            address="Санкт-Петербург",
            description="Главный корпус",
        )
        self.conference = Conference.objects.create(
            name="SciConf 2026",
            location=location,
            start_date="2026-11-10",
            end_date="2026-11-12",
            participation_terms="Подать тезисы до 1 ноября",
        )
        self.author = get_user_model().objects.create_user(
            username="talk_author",
            password="Strong-test-password-739!",
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("submit_talk", args=[self.conference.pk])
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('submit_talk', args=[self.conference.pk])}",
        )

    def test_authenticated_user_can_open_submission_form(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("submit_talk", args=[self.conference.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conference.name)
        self.assertContains(response, "Название доклада")

    def test_valid_submission_is_bound_to_current_user_and_conference(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("submit_talk", args=[self.conference.pk]),
            {
                "title": "Новые методы анализа данных",
                "abstract": "Доклад о применении современных методов.",
                "author": 99999,
                "conference": 99999,
            },
        )

        self.assertRedirects(
            response,
            reverse("conference_detail", args=[self.conference.pk]),
        )
        submission = TalkSubmission.objects.get()
        self.assertEqual(submission.author, self.author)
        self.assertEqual(submission.conference, self.conference)
        self.assertEqual(submission.title, "Новые методы анализа данных")

    def test_invalid_submission_is_not_saved(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("submit_talk", args=[self.conference.pk]),
            {"title": "", "abstract": "Аннотация"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TalkSubmission.objects.exists())

    def test_owner_can_edit_own_submission(self):
        submission = TalkSubmission.objects.create(
            title="Старое название",
            abstract="Старая аннотация",
            conference=self.conference,
            author=self.author,
            recommended_to_publish=True,
        )
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("edit_talk", args=[submission.pk]),
            {"title": "Новое название", "abstract": "Новая аннотация"},
        )

        self.assertRedirects(
            response,
            reverse("conference_detail", args=[self.conference.pk]),
        )
        submission.refresh_from_db()
        self.assertEqual(submission.title, "Новое название")
        self.assertEqual(submission.abstract, "Новая аннотация")
        self.assertTrue(submission.recommended_to_publish)

    def test_other_user_cannot_edit_or_delete_submission(self):
        submission = TalkSubmission.objects.create(
            title="Чужой доклад",
            abstract="Аннотация",
            conference=self.conference,
            author=self.author,
        )
        other_user = get_user_model().objects.create_user(
            username="another_author",
            password="Strong-test-password-739!",
        )
        self.client.force_login(other_user)

        edit_response = self.client.get(reverse("edit_talk", args=[submission.pk]))
        delete_response = self.client.get(reverse("delete_talk", args=[submission.pk]))

        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertTrue(TalkSubmission.objects.filter(pk=submission.pk).exists())

    def test_owner_must_confirm_deletion_with_post(self):
        submission = TalkSubmission.objects.create(
            title="Доклад для удаления",
            abstract="Аннотация",
            conference=self.conference,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.get(reverse("delete_talk", args=[submission.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Да, удалить")
        self.assertTrue(TalkSubmission.objects.filter(pk=submission.pk).exists())

    def test_owner_can_delete_submission_with_post(self):
        submission = TalkSubmission.objects.create(
            title="Доклад для удаления",
            abstract="Аннотация",
            conference=self.conference,
            author=self.author,
        )
        self.client.force_login(self.author)

        response = self.client.post(reverse("delete_talk", args=[submission.pk]))

        self.assertRedirects(
            response,
            reverse("conference_detail", args=[self.conference.pk]),
        )
        self.assertFalse(TalkSubmission.objects.filter(pk=submission.pk).exists())


class ParticipantListViewTests(TestCase):
    def setUp(self):
        location = Location.objects.create(
            name="Университет",
            address="Санкт-Петербург",
            description="Главный корпус",
        )
        self.conference = Conference.objects.create(
            name="SciConf Admin Test",
            location=location,
            start_date="2027-03-10",
            end_date="2027-03-11",
            participation_terms="Условия",
        )
        self.author = get_user_model().objects.create_user(
            username="participant",
            email="participant@example.com",
            password="Strong-test-password-739!",
        )
        self.submission = TalkSubmission.objects.create(
            title="Demo participant talk",
            abstract="Talk abstract",
            conference=self.conference,
            author=self.author,
        )

    def test_staff_user_sees_participants_table(self):
        admin_user = get_user_model().objects.create_user(
            username="staff_admin",
            password="Strong-test-password-739!",
            is_staff=True,
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("participant_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conference.name)
        self.assertContains(response, self.author.username)
        self.assertContains(response, self.submission.title)
        self.assertContains(response, "На рассмотрении")
        self.assertContains(response, reverse("participant_list"))

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("participant_list"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('participant_list')}",
        )

    def test_non_staff_user_cannot_access_participants_table(self):
        regular_user = get_user_model().objects.create_user(
            username="regular_user",
            password="Strong-test-password-739!",
        )
        self.client.force_login(regular_user)

        response = self.client.get(reverse("participant_list"))

        self.assertEqual(response.status_code, 403)

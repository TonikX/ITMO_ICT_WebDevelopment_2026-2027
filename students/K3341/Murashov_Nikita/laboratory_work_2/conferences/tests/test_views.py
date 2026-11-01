"""Страницы целиком: отрисовка, формы, сценарии пользователя и администратора."""
from datetime import date

from django.urls import reverse

from conferences.models import Conference, Participation, Review, User

from .base import PASSWORD, BaseTestCase, make_conference, make_participation, make_review


class PublicPagesTests(BaseTestCase):
    def test_pages_render(self):
        self.assertContains(self.client.get(reverse("conference-list")), "Конф А")
        self.assertContains(self.client.get(self.conf.get_absolute_url()), "Условия")
        self.assertEqual(self.client.get(reverse("participants")).status_code, 200)
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("register")).status_code, 200)

    def test_missing_conference_is_404(self):
        self.assertEqual(self.client.get(reverse("conference-detail", args=[999999])).status_code, 404)

    def test_search_and_filter_form_values_are_kept(self):
        r = self.client.get(reverse("conference-list"), {"q": "конф", "sort": "title"})
        self.assertContains(r, 'value="конф"')
        self.assertContains(r, '<option value="title" selected>')


class ListPaginationTests(BaseTestCase):
    CARD = '<h2 class="h5">'  # заголовок карточки конференции в списке

    def test_five_per_page_and_filters_in_links(self):
        for i in range(7):
            make_conference(f"Доп {i}", city="Казань", start_date=date(2031, 1, 1), end_date=date(2031, 1, 2))
        url = reverse("conference-list")
        self.assertEqual(self.client.get(url).content.decode().count(self.CARD), 5)
        self.assertEqual(self.client.get(url, {"page": 2}).content.decode().count(self.CARD), 3)
        html = self.client.get(url, {"city": "Казань"}).content.decode()
        self.assertRegex(html, r'href="\?[^"]*city=[^"]*page=2"')

    def test_sorting_on_page(self):
        other = make_conference("Ярче", start_date=date(2029, 1, 1), end_date=date(2029, 1, 2))
        url = reverse("conference-list")

        def first_is_conf(**params):
            html = self.client.get(url, params).content.decode()
            return html.index(f'href="/conferences/{self.conf.pk}/"') < html.index(f'href="/conferences/{other.pk}/"')

        self.assertFalse(first_is_conf())
        self.assertTrue(first_is_conf(sort="-date"))

    def test_garbage_parameters_do_not_break_pages(self):
        garbage = {"sort": "id; DROP TABLE", "date_from": "abc", "date_to": "2024-13-45", "topic": "²"}
        self.assertContains(self.client.get(reverse("conference-list"), garbage), "Конф А")
        participants = self.client.get(reverse("participants"), {"conference": "²", "result": "?"})
        self.assertEqual(participants.status_code, 200)

    def test_bad_page_number_is_404(self):
        self.assertEqual(self.client.get(reverse("conference-list"), {"page": "x"}).status_code, 404)


class SignUpTests(BaseTestCase):
    def test_register_creates_user_with_profile_fields_and_logs_in(self):
        r = self.client.post(
            reverse("register"),
            {
                "username": "new", "first_name": "Н", "last_name": "О", "email": "n@e.ru",
                "organization": "ИТМО", "academic_degree": "к.т.н.",
                "password1": PASSWORD, "password2": PASSWORD,
            },
        )
        self.assertRedirects(r, reverse("conference-list"))
        user = User.objects.get(username="new")
        self.assertEqual((user.organization, user.academic_degree), ("ИТМО", "к.т.н."))
        self.assertContains(self.client.get(reverse("conference-list")), "Выйти")

    def test_password_mismatch_is_rejected(self):
        self.client.post(reverse("register"), {"username": "bad", "password1": PASSWORD, "password2": PASSWORD + "x"})
        self.assertFalse(User.objects.filter(username="bad").exists())


class ParticipationFlowTests(BaseTestCase):
    def test_register_edit_delete(self):
        self.login("user")
        url = reverse("participation-create", args=[self.conf.pk])
        self.client.post(url, {"talk_title": "T", "abstract": "A"})
        p = Participation.objects.get()
        self.assertEqual((p.user, p.result), (self.user, Participation.Result.PENDING))
        self.client.post(url, {"talk_title": "T2", "abstract": "A2"})  # повтор не создаёт дубль
        self.assertEqual(Participation.objects.count(), 1)
        self.client.post(reverse("participation-update", args=[p.pk]), {"talk_title": "New", "abstract": "A"})
        p.refresh_from_db()
        self.assertEqual(p.talk_title, "New")
        self.client.post(reverse("participation-delete", args=[p.pk]))
        self.assertFalse(Participation.objects.exists())

    def test_second_visit_to_form_redirects_to_conference(self):
        make_participation(self.conf, self.user)
        self.login("user")
        r = self.client.get(reverse("participation-create", args=[self.conf.pk]))
        self.assertRedirects(r, self.conf.get_absolute_url())

    def test_author_can_edit_and_delete_after_decision_and_result_is_kept(self):
        # По заданию автор вправе редактировать и удалять свою регистрацию, ограничений по статусу нет.
        p = make_participation(self.conf, self.user, result=Participation.Result.RECOMMENDED)
        self.login("user")
        self.client.post(reverse("participation-update", args=[p.pk]), {"talk_title": "Правка", "abstract": "A"})
        p.refresh_from_db()
        self.assertEqual((p.talk_title, p.result), ("Правка", Participation.Result.RECOMMENDED))
        self.client.post(reverse("participation-delete", args=[p.pk]))
        self.assertFalse(Participation.objects.exists())

    def test_my_participations_shows_only_own_and_edit_buttons(self):
        mine = make_participation(self.conf, self.user, result=Participation.Result.NOT_RECOMMENDED)
        make_participation(self.conf, self.other, talk_title="Чужой")
        self.login("user")
        r = self.client.get(reverse("my-participations"))
        self.assertNotContains(r, "Чужой")
        self.assertContains(r, reverse("participation-update", args=[mine.pk]))
        self.assertContains(r, reverse("participation-delete", args=[mine.pk]))


class StaffClientTests(BaseTestCase):
    def test_staff_sets_result(self):
        p = make_participation(self.conf, self.user)
        self.login("staff")
        r = self.client.post(reverse("participation-result", args=[p.pk]), {"result": "recommended"})
        self.assertRedirects(r, reverse("participants") + f"?conference={self.conf.pk}")
        p.refresh_from_db()
        self.assertEqual(p.result, Participation.Result.RECOMMENDED)

    def test_staff_creates_conference(self):
        self.login("staff")
        r = self.client.post(
            reverse("conference-create"),
            {
                "title": "Новая", "topics": [self.topic.id], "venue_name": "V", "city": "C",
                "start_date": "2031-01-01", "end_date": "2031-01-02",
                "description": "d", "venue_description": "", "participation_terms": "t",
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(list(Conference.objects.get(title="Новая").topics.all()), [self.topic])

    def test_invalid_period_is_rejected_with_message(self):
        self.login("staff")
        r = self.client.post(
            reverse("conference-create"),
            {
                "title": "Плохая", "venue_name": "V", "city": "C", "start_date": "2031-02-01",
                "end_date": "2031-01-01", "description": "d", "participation_terms": "t",
            },
        )
        self.assertContains(r, "Дата окончания не может быть раньше начала")
        self.assertFalse(Conference.objects.filter(title="Плохая").exists())

    def test_admin_buttons_visible_only_for_staff(self):
        url = self.conf.get_absolute_url()
        delete_href = reverse("conference-delete", args=[self.conf.pk])
        self.assertNotContains(self.client.get(url), delete_href)
        self.login("user")
        self.assertNotContains(self.client.get(url), delete_href)
        self.login("staff")
        self.assertContains(self.client.get(url), delete_href)


class ParticipantsTableTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.conf2 = make_conference("Конф Б", start_date=date(2031, 1, 1), end_date=date(2031, 1, 2))
        make_participation(cls.conf, cls.user, talk_title="Нейросети")
        make_participation(cls.conf2, cls.other, talk_title="Веб")

    def test_one_table_per_conference(self):
        html = self.client.get(reverse("participants")).content.decode()
        self.assertEqual(html.count("<table"), 2)
        # названия есть и в выпадающем списке, поэтому смотрим на ссылки в заголовках и ячейки таблиц
        a, b = (f'class="fw-semibold text-decoration-none" href="{c.get_absolute_url()}"' for c in (self.conf, self.conf2))
        self.assertLess(html.index(a), html.index("<td>Нейросети</td>"))
        self.assertLess(html.index("<td>Нейросети</td>"), html.index(b))
        self.assertLess(html.index(b), html.index("<td>Веб</td>"))

    def test_search_and_conference_filter(self):
        url = reverse("participants")
        r = self.client.get(url, {"q": "Нейро"})
        self.assertContains(r, "Иванов")
        self.assertNotContains(r, "Конф Б</a>")
        self.assertContains(self.client.get(url, {"conference": self.conf2.pk}), "Веб")
        self.assertContains(self.client.get(url, {"q": "zzz"}), "Участников не найдено")

    def test_pagination_is_by_conferences(self):
        for i in range(3):
            c = make_conference(f"Ещё {i}", start_date=date(2032, 1, 1 + i), end_date=date(2032, 1, 2 + i))
            make_participation(c, self.user)
        url = reverse("participants")
        self.assertEqual(self.client.get(url).content.decode().count("<table"), 3)
        self.assertEqual(self.client.get(url, {"page": 2}).content.decode().count("<table"), 2)

    def test_result_column_only_for_staff(self):
        url = reverse("participants")
        self.assertNotContains(self.client.get(url), "Результат</a>")
        self.login("staff")
        self.assertContains(self.client.get(url), "Результат</a>")


class ReviewFlowTests(BaseTestCase):
    def test_create_review_with_author_data(self):
        self.login("user")
        url = reverse("review-create", args=[self.conf.pk])
        data = {"start_date": "2030-05-01", "end_date": "2030-05-03", "text": "Отлично", "rating": 9}
        self.client.post(url, data)
        review = Review.objects.get()
        self.assertEqual((review.author, review.rating), (self.user, 9))
        page = self.client.get(self.conf.get_absolute_url())
        self.assertContains(page, "Отлично")
        self.assertContains(page, "Иван Иванов")
        self.assertContains(page, "ИТМО")

    def test_rating_bounds_in_form(self):
        self.login("user")
        url = reverse("review-create", args=[self.conf.pk])
        for bad in (0, 11):
            self.client.post(url, {"start_date": "2030-05-01", "end_date": "2030-05-03", "text": "t", "rating": bad})
        self.assertFalse(Review.objects.exists())

    def test_end_before_start_in_form(self):
        self.login("user")
        self.client.post(
            reverse("review-create", args=[self.conf.pk]),
            {"start_date": "2030-05-03", "end_date": "2030-05-01", "text": "t", "rating": 5},
        )
        self.assertFalse(Review.objects.exists())

    def test_average_rating_is_shown(self):
        make_review(self.conf, self.user, rating=8)
        make_review(self.conf, self.other, rating=9)
        self.assertContains(self.client.get(self.conf.get_absolute_url()), "8.5/10")

"""Бизнес-логика: выборки, поиск, фильтры, сортировка, регистрация авторов."""
from datetime import date

from django.contrib.auth.models import AnonymousUser
from django.http import QueryDict

from conferences import services
from conferences.forms import ConferenceFilter, ParticipantFilter
from conferences.models import Participation

from .base import BaseTestCase, clean_filters, make_conference, make_participation, make_review


class SearchConferencesTests(BaseTestCase):
    def titles(self, **params):
        filters = clean_filters(ConferenceFilter, **params)
        return [c.title for c in services.search_conferences(filters)]

    def test_search_by_text_and_topic_name(self):
        self.assertEqual(self.titles(q="конф"), ["Конф А"])
        self.assertEqual(self.titles(q="ИИ"), ["Конф А"])
        self.assertEqual(self.titles(q="нет такого"), [])

    def test_filter_by_topic(self):
        self.assertEqual(self.titles(topic=self.topic.pk), ["Конф А"])
        self.assertEqual(self.titles(topic=self.other_topic.pk), [])

    def test_filter_by_city_and_dates(self):
        self.assertEqual(self.titles(city="москва"), ["Конф А"])
        self.assertEqual(self.titles(city="Казань"), [])
        self.assertEqual(self.titles(date_from="2031-01-01"), [])
        self.assertEqual(self.titles(date_to="2029-01-01"), [])

    def test_garbage_filters_are_dropped(self):
        for params in (
            {"date_from": "abc"}, {"date_to": "2024-13-45"}, {"topic": "²"},
            {"topic": "99999"}, {"sort": "id; DROP TABLE"},
        ):
            with self.subTest(params=params):
                self.assertEqual(self.titles(**params), ["Конф А"])

    def test_annotations(self):
        make_review(self.conf, self.user, rating=8)
        make_review(self.conf, self.other, rating=10)
        make_participation(self.conf, self.user)
        conf = services.search_conferences({}).get()
        self.assertEqual(conf.avg_rating, 9)
        self.assertEqual(conf.participants_count, 1)


class SortingTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # «Конф А»: 2030 год, с оценкой; «Ярче»: 2029 год, без оценок
        make_conference("Ярче", start_date=date(2029, 1, 1), end_date=date(2029, 1, 2))
        make_review(cls.conf, cls.user, rating=9)

    def titles(self, **params):
        return [c.title for c in services.search_conferences(clean_filters(ConferenceFilter, **params))]

    def test_default_is_nearest_first(self):
        self.assertEqual(self.titles(), ["Ярче", "Конф А"])

    def test_options(self):
        self.assertEqual(self.titles(sort="-date"), ["Конф А", "Ярче"])
        self.assertEqual(self.titles(sort="title"), ["Конф А", "Ярче"])
        self.assertEqual(self.titles(sort="rating"), ["Конф А", "Ярче"])  # без оценки в конце

    def test_filter_options_lists_all_sort_keys(self):
        keys = [key for key, _ in services.filter_options()["sort_options"]]
        self.assertEqual(keys, list(services.SORT_OPTIONS))


class QuerystringTests(BaseTestCase):
    def test_page_is_dropped_and_filters_kept(self):
        self.assertEqual(services.querystring_without_page(QueryDict("q=x&page=3")), "q=x")

    def test_original_params_untouched(self):
        params = QueryDict("q=x&page=3")
        services.querystring_without_page(params)
        self.assertEqual(params["page"], "3")


class ReviewHelpersTests(BaseTestCase):
    def test_average_rating(self):
        self.assertIsNone(services.average_rating(self.conf))
        make_review(self.conf, self.user, rating=7)
        make_review(self.conf, self.other, rating=8)
        self.assertEqual(services.average_rating(self.conf), 7.5)


class RegisterAuthorTests(BaseTestCase):
    def test_creates_once(self):
        first, created = services.register_author(self.conf, self.user, "Т1", "А1")
        self.assertTrue(created)
        self.assertEqual(first.result, Participation.Result.PENDING)
        second, created = services.register_author(self.conf, self.user, "Т2", "А2")
        self.assertFalse(created)
        self.assertEqual((second.pk, second.talk_title), (first.pk, "Т1"))
        self.assertEqual(Participation.objects.count(), 1)

    def test_get_participation(self):
        self.assertIsNone(services.get_participation(self.conf, self.user))
        p = make_participation(self.conf, self.user)
        self.assertEqual(services.get_participation(self.conf, self.user), p)
        self.assertIsNone(services.get_participation(self.conf, AnonymousUser()))


class ParticipantsTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.conf2 = make_conference("Конф Б", start_date=date(2031, 1, 1), end_date=date(2031, 1, 2))
        make_conference("Пустая", start_date=date(2032, 1, 1), end_date=date(2032, 1, 2))
        cls.p1 = make_participation(cls.conf, cls.user, talk_title="Нейросети")
        cls.p2 = make_participation(cls.conf, cls.other, talk_title="СУБД", result=Participation.Result.RECOMMENDED)
        cls.p3 = make_participation(cls.conf2, cls.user, talk_title="Веб")

    def found(self, **params):
        filters = clean_filters(ParticipantFilter, **params)
        return {p.pk for p in services.filter_participations(filters)}

    def test_filters(self):
        everyone = {self.p1.pk, self.p2.pk, self.p3.pk}
        self.assertEqual(self.found(), everyone)
        self.assertEqual(self.found(conference=self.conf2.pk), {self.p3.pk})
        self.assertEqual(self.found(result="recommended"), {self.p2.pk})
        self.assertEqual(self.found(q="Нейро"), {self.p1.pk})
        self.assertEqual(self.found(q="ИТМО"), {self.p1.pk, self.p3.pk})

    def test_garbage_filters_are_dropped(self):
        everyone = self.found()
        self.assertEqual(self.found(result="bogus"), everyone)
        self.assertEqual(self.found(conference="²"), everyone)

    def test_only_conferences_with_participants_in_date_order(self):
        confs = services.conferences_with_participants(Participation.objects.all())
        self.assertEqual([c.title for c in confs], ["Конф А", "Конф Б"])

    def test_grouping_respects_filter(self):
        participations = services.filter_participations({})
        groups = services.group_by_conference(services.conferences_with_participants(participations), participations)
        self.assertEqual(
            {c.title: {p.pk for p in rows} for c, rows in groups},
            {"Конф А": {self.p1.pk, self.p2.pk}, "Конф Б": {self.p3.pk}},
        )
        recommended = services.filter_participations({"result": "recommended"})
        groups = services.group_by_conference(services.conferences_with_participants(recommended), recommended)
        self.assertEqual([(c.title, [p.pk for p in rows]) for c, rows in groups], [("Конф А", [self.p2.pk])])

import secrets
from datetime import date

from django.test import TestCase

from conferences.models import Conference, Participation, Review, Topic, User

PASSWORD = secrets.token_urlsafe(16)  # пароли в тестах случайные


def make_conference(title="Конф А", **kwargs):
    defaults = dict(
        city="Москва",
        venue_name="МГУ",
        start_date=date(2030, 5, 1),
        end_date=date(2030, 5, 3),
        description="Описание",
        participation_terms="Условия",
    )
    defaults.update(kwargs)
    return Conference.objects.create(title=title, **defaults)


def make_participation(conference, user, **kwargs):
    defaults = dict(talk_title="Доклад", abstract="Тезисы")
    defaults.update(kwargs)
    return Participation.objects.create(conference=conference, user=user, **defaults)


def make_review(conference, author, rating=8, **kwargs):
    defaults = dict(start_date=date(2030, 5, 1), end_date=date(2030, 5, 2), text="Текст")
    defaults.update(kwargs)
    return Review.objects.create(conference=conference, author=author, rating=rating, **defaults)


def clean_filters(form_class, **params):
    """То, что получает services после проверки GET-параметров формой-фильтром."""
    form = form_class(params)
    form.is_valid()
    return form.cleaned_data


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = Topic.objects.create(name="ИИ")
        cls.other_topic = Topic.objects.create(name="Базы данных")
        cls.conf = make_conference()
        cls.conf.topics.add(cls.topic)
        cls.user = User.objects.create_user(
            "user", password=PASSWORD, first_name="Иван", last_name="Иванов", organization="ИТМО"
        )
        cls.other = User.objects.create_user("other", password=PASSWORD)
        cls.staff = User.objects.create_user("staff", password=PASSWORD, is_staff=True)

    def login(self, username):
        self.assertTrue(self.client.login(username=username, password=PASSWORD))

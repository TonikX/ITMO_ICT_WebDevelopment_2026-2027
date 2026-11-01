"""Демо-данные: команда `seed` не дублирует записи и не хранит паролей в коде."""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from conferences.models import Conference, Participation, Review, User


class SeedTests(TestCase):
    def run_seed(self):
        out = StringIO()
        call_command("seed", stdout=out)
        return out.getvalue()

    def test_creates_data_and_is_idempotent(self):
        first = self.run_seed()
        counts = (User.objects.count(), Conference.objects.count(), Participation.objects.count(), Review.objects.count())
        self.assertEqual(counts[:2], (5, 7))
        self.assertIn("admin /", first)
        second = self.run_seed()
        self.assertNotIn("/", second)  # пароли печатаются только у созданных пользователей
        self.assertEqual(counts, (User.objects.count(), Conference.objects.count(), Participation.objects.count(), Review.objects.count()))

    def test_reviews_exist_only_for_past_conferences(self):
        self.run_seed()
        for review in Review.objects.select_related("conference"):
            self.assertLess(review.conference.end_date, review.created_at.date())

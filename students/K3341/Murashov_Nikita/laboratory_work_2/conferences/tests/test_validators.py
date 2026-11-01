"""Защита данных: проверки значений."""
from datetime import date

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from conferences.validators import RATING_MAX, RATING_MIN, RATING_VALIDATORS, validate_date_range

from .base import BaseTestCase, make_conference, make_review


class DateRangeTests(SimpleTestCase):
    def test_valid_ranges(self):
        validate_date_range(date(2030, 1, 1), date(2030, 1, 1))
        validate_date_range(date(2030, 1, 1), date(2030, 1, 5))

    def test_end_before_start_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_date_range(date(2030, 2, 1), date(2030, 1, 1))
        self.assertIn("end_date", ctx.exception.message_dict)

    def test_missing_dates_are_not_checked_here(self):
        validate_date_range(None, date(2030, 1, 1))
        validate_date_range(date(2030, 1, 1), None)


class RatingTests(SimpleTestCase):
    def check(self, value):
        for validator in RATING_VALIDATORS:
            validator(value)

    def test_bounds_are_inclusive(self):
        self.check(RATING_MIN)
        self.check(RATING_MAX)

    def test_out_of_range_is_rejected(self):
        for bad in (RATING_MIN - 1, RATING_MAX + 1, 100):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                self.check(bad)


class ModelValidationTests(BaseTestCase):
    def test_conference_clean(self):
        conf = make_conference("Плохая", start_date=date(2031, 2, 1), end_date=date(2031, 1, 1))
        with self.assertRaises(ValidationError):
            conf.full_clean()

    def test_review_clean(self):
        review = make_review(self.conf, self.user, start_date=date(2030, 5, 3), end_date=date(2030, 5, 1))
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_review_rating_validated_by_model(self):
        review = make_review(self.conf, self.user, rating=11)
        with self.assertRaises(ValidationError) as ctx:
            review.full_clean()
        self.assertIn("rating", ctx.exception.message_dict)

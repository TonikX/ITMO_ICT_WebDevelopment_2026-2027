"""Защита данных: проверки значений. Не знают ни про представления, ни про запросы."""
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

RATING_MIN = 1
RATING_MAX = 10
RATING_VALIDATORS = [MinValueValidator(RATING_MIN), MaxValueValidator(RATING_MAX)]


def validate_date_range(start, end):
    """Дата окончания не может быть раньше даты начала."""
    if start and end and end < start:
        raise ValidationError({"end_date": "Дата окончания не может быть раньше начала."})

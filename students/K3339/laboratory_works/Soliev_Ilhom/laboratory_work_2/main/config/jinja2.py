from django.templatetags.static import static
from django.urls import reverse
from django.utils.formats import date_format, number_format
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(static=static, url=reverse)
    env.filters["date"] = lambda value: date_format(value, "d.m.Y")
    env.filters["money"] = lambda value: number_format(value, decimal_pos=0, force_grouping=True)
    return env

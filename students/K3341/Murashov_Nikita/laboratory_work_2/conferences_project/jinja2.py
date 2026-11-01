from django.urls import reverse
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals["url"] = reverse
    env.filters["date"] = lambda value: value.strftime("%d.%m.%Y")
    return env

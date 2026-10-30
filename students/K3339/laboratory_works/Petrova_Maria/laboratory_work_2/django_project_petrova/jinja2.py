from django.templatetags.static import static
from django.urls import reverse
from django.utils.formats import localize
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(url=reverse, static=static)
    env.filters['localize'] = localize
    return env

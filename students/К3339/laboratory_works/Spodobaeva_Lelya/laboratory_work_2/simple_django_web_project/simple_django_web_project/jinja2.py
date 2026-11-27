from django.urls import reverse
from django.utils.formats import localize
from jinja2 import Environment


def url(name, *args):
    return reverse(name, args=args)


def environment(**options):
    env = Environment(**options)
    env.globals["url"] = url
    env.filters["localize"] = localize
    return env

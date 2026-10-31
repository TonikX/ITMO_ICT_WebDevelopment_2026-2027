from django.contrib.messages import get_messages
from django.template.defaultfilters import floatformat
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(url=reverse, static=static, get_messages=get_messages)
    env.filters["price"] = lambda value: floatformat(value, "-2g")
    return env

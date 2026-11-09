from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils import formats, timezone
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(static=staticfiles_storage.url, url=reverse)
    env.filters['date'] = lambda value, pattern='d.m.Y': formats.date_format(timezone.localtime(value), pattern) if value else '—'
    env.filters['money'] = lambda value: f'{value:,.0f}'.replace(',', ' ')
    return env

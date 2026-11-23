from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(static=static, url=reverse)
    env.filters['datetime'] = lambda value: timezone.localtime(value).strftime('%d.%m.%Y · %H:%M') if value else '—'
    env.filters['date'] = lambda value, fmt='%d.%m.%Y': (timezone.localtime(value) if getattr(value, 'tzinfo', None) else value).strftime(fmt) if value else '—'
    return env

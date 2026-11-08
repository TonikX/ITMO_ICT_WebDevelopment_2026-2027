from datetime import datetime
from django.contrib import messages
from django.templatetags.static import static
from django.urls import reverse
from django.utils.formats import date_format
from django.utils import timezone
from jinja2 import Environment


def race_time(value):
    if value is None:
        return '—'
    milliseconds = round(value.total_seconds() * 1000)
    minutes, rest = divmod(milliseconds, 60000)
    seconds, ms = divmod(rest, 1000)
    return f'{minutes:02d}:{seconds:02d}.{ms:03d}'


def display_date(value, fmt='d.m.Y'):
    if isinstance(value, datetime) and timezone.is_aware(value):
        value = timezone.localtime(value)
    return date_format(value, fmt)


def photo_srcset(name):
    original_width = 2000 if name == 'race-orange.webp' else 1100
    variants = [480, 800] + ([1200] if original_width > 1200 else [])
    files = [(name.replace('.webp', f'-{width}.webp'), width) for width in variants]
    files.append((name, original_width))
    return ', '.join(f'{static("images/" + filename)} {width}w' for filename, width in files)


def environment(**options):
    env = Environment(**options)
    env.globals.update(static=static, url=reverse, get_messages=messages.get_messages, photo_srcset=photo_srcset)
    env.filters.update(date=display_date, race_time=race_time)
    return env

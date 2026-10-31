"""Глобальные функции пользовательских шаблонов Jinja2."""

from django.contrib.messages import get_messages
from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment


def environment(**options) -> Environment:
    """Создаёт окружение с адресацией Django и сообщениями."""
    env = Environment(**options)
    env.globals.update(url=reverse, static=static, get_messages=get_messages)
    return env

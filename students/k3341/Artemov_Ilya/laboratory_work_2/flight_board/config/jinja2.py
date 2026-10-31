from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from jinja2 import Environment


def url(name, *args, **kwargs):
    return reverse(name, args=args or None, kwargs=kwargs or None)


def page_url(request, page):
    params = request.GET.copy()
    params["page"] = page
    return "?" + params.urlencode()


def date_time(value):
    if not value:
        return "—"
    return timezone.localtime(value).strftime("%d.%m.%Y %H:%M")


def is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def environment(**options):
    env = Environment(**options)
    env.globals.update(static=static, url=url, page_url=page_url, is_staff=is_staff)
    env.filters["date_time"] = date_time
    return env


from jinja2 import Environment
from django.urls import reverse
from django.templatetags.static import static


def url(viewname, **kwargs):
    return reverse(viewname, kwargs=kwargs or None)


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        "url": url,
        "static": static,
    })
    return env

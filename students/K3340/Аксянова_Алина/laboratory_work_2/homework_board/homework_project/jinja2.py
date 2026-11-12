from jinja2 import Environment
from django.urls import reverse
from django.templatetags.static import static
from django.contrib.messages import get_messages

def environment(**options):
    env = Environment(**options)

    env.globals.update({
        'url': reverse,
        'static': static,
        'get_messages': get_messages,
    })

    return env

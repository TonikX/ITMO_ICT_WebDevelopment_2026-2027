from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.messages import get_messages
from django.urls import reverse

def page_url(request, number):
    params = request.GET.copy()
    params['page'] = number
    return '?' + params.urlencode()

def environment(**options):
    env = Environment(**options)
    env.globals.update(static=staticfiles_storage.url, url=reverse,
                       messages=get_messages, page_url=page_url)
    return env

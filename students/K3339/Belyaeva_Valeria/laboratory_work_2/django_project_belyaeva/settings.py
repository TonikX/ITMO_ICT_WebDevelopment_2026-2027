import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'local-development-nordline-laboratory-only')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'flights', 'project_first_app',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'django_project_belyaeva.urls'
TEMPLATES = [
    {'BACKEND': 'django.template.backends.jinja2.Jinja2', 'DIRS': [BASE_DIR / 'templates'],
     'APP_DIRS': True, 'OPTIONS': {'environment': 'django_project_belyaeva.jinja2.environment',
     'context_processors': ['django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages']}},
    {'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
     'OPTIONS': {'context_processors': ['django.template.context_processors.request',
                 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}},
]
WSGI_APPLICATION = 'django_project_belyaeva.wsgi.application'
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql', 'NAME': os.environ.get('PGDATABASE', 'nordline'),
    'USER': os.environ.get('PGUSER', 'web_lab'), 'PASSWORD': os.environ.get('PGPASSWORD', ''),
    'HOST': os.environ.get('PGHOST', '127.0.0.1'), 'PORT': os.environ.get('PGPORT', '55432'),
}}
AUTH_USER_MODEL = 'flights.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'bookings'
LOGOUT_REDIRECT_URL = 'flight_list'

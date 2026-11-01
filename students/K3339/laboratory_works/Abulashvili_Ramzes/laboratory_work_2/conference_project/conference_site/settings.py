import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "database.local.json"
if not CONFIG_FILE.exists():
    CONFIG_FILE = BASE_DIR.parent / "database.local.json"
DATABASE_CONFIG = json.loads(CONFIG_FILE.read_text(encoding="utf-8")) if CONFIG_FILE.exists() else {}
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-web-lab-2-local-development")
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "conferences",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "conference_site.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    },
]
WSGI_APPLICATION = "conference_site.wsgi.application"
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "web_lab_2_conferences",
    "USER": DATABASE_CONFIG.get("user", "web_lab_2"),
    "PASSWORD": DATABASE_CONFIG.get("password", ""),
    "HOST": DATABASE_CONFIG.get("host", "127.0.0.1"),
    "PORT": DATABASE_CONFIG.get("port", 5432),
}}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
SESSION_COOKIE_NAME = "conference_sessionid"
CSRF_COOKIE_NAME = "conference_csrftoken"
LOGIN_REDIRECT_URL = "conference_list"
LOGOUT_REDIRECT_URL = "conference_list"
TEMPLATES.insert(0, {
    "BACKEND": "django.template.backends.jinja2.Jinja2",
    "DIRS": [BASE_DIR / "jinja2"],
    "APP_DIRS": True,
    "OPTIONS": {"environment": "conference_site.jinja2.environment"},
})

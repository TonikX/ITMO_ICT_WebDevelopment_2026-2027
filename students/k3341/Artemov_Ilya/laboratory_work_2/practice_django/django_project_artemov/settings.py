import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "local-practice-only-change-before-deployment")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "project_first_app",
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
ROOT_URLCONF = "django_project_artemov.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "django_project_artemov.wsgi.application"
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("DB_NAME", "web_lab2_practice"),
    "USER": os.environ.get("DB_USER", "web_lab2"),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
    "PORT": os.environ.get("DB_PORT", "5432"),
}}
AUTH_USER_MODEL = "project_first_app.CarOwner"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{name}"}
    for name in ["UserAttributeSimilarityValidator", "MinimumLengthValidator",
                 "CommonPasswordValidator", "NumericPasswordValidator"]
]
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "owners"
LOGOUT_REDIRECT_URL = "owners"
SESSION_COOKIE_NAME = "practice_sessionid"
CSRF_COOKIE_NAME = "practice_csrftoken"

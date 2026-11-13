import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
SECRET_KEY = os.getenv('SECRET_KEY', 'local-lab-only-change-before-deployment-123456789')
DEBUG = os.getenv('DEBUG', '1') == '1'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]').split(',')
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'accounts', 'tours', 'project_first_app']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware',
 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware',
 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware',
 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'django_project_student.urls'
TEMPLATES = [
 {'BACKEND': 'django.template.backends.jinja2.Jinja2', 'DIRS': [BASE_DIR / 'templates'],
  'APP_DIRS': True, 'OPTIONS': {'environment': 'django_project_student.jinja2.environment'}},
 {'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
  'OPTIONS': {'context_processors': ['django.template.context_processors.debug',
  'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
  'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'django_project_student.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql',
 'NAME': os.getenv('POSTGRES_DB','tour_agency'), 'USER': os.getenv('POSTGRES_USER','tour_user'),
 'PASSWORD': os.getenv('POSTGRES_PASSWORD','tour_local_password'),
 'HOST': os.getenv('POSTGRES_HOST','127.0.0.1'), 'PORT': os.getenv('POSTGRES_PORT','5432')}}
AUTH_USER_MODEL = 'accounts.User'
AUTH_PASSWORD_VALIDATORS = [
 {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
 {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'tour_list'
LOGOUT_REDIRECT_URL = 'tour_list'

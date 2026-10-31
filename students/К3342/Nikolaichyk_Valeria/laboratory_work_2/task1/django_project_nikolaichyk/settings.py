
from pathlib import Path

# Определяем базовую директорию проекта.
# Через BASE_DIR Django будет находить файлы и папки проекта.
BASE_DIR = Path(__file__).resolve().parent.parent


# Секретный ключ проекта.
# Используется Django для защиты сессий и других механизмов безопасности.
# Не следует публиковать этот ключ в открытом доступе.
SECRET_KEY = 'django-insecure-5ka5wr8h3@f&karg5z3ko+s7_n%+_b7^(^ei&soanfa%a6vetq'


# Режим отладки.
# True — подробные сообщения об ошибках при разработке.
# На опубликованном сайте необходимо установить False.
DEBUG = True

# Список адресов, с которых разрешено обращаться к приложению.
# Пустой список допустим для текущей локальной разработки.
ALLOWED_HOSTS = []


# Подключённые приложения проекта.
# Здесь перечисляются встроенные приложения Django и наше приложение project_first_app.
INSTALLED_APPS = [
    'django.contrib.admin',       # Административная панель
    'django.contrib.auth',        # Авторизация и пользователи
    'django.contrib.contenttypes',# Работа с типами моделей
    'django.contrib.sessions',    # Хранение пользовательских сессий
    'django.contrib.messages',    # Система уведомлений
    'django.contrib.staticfiles', # Статические файлы (CSS, JavaScript, изображения)
    'project_first_app',                       # приложение с туристическими турами
]


# Промежуточные обработчики запросов (middleware).
# Они выполняют дополнительные действия при обработке HTTP-запросов.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',          # Защита сайта
    'django.contrib.sessions.middleware.SessionMiddleware',  # Поддержка сессий
    'django.middleware.common.CommonMiddleware',              # Общие функции обработки запросов
    'django.middleware.csrf.CsrfViewMiddleware',              # Защита от CSRF-атак
    'django.contrib.auth.middleware.AuthenticationMiddleware',# Определение пользователя
    'django.contrib.messages.middleware.MessageMiddleware',   # Передача уведомлений
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Защита от clickjacking
]


# Указываем расположение главного файла маршрутизации проекта.
ROOT_URLCONF = 'django_project_nikolaichyk.urls'


# Настройки системы шаблонов.
# Django использует HTML-шаблоны для отображения страниц пользователю.
TEMPLATES = [
    {
        # Используем встроенный движок шаблонов Django.
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Дополнительные папки для поиска шаблонов.
        'DIRS': [],

        # Разрешаем искать шаблоны внутри папок templates приложений.
        'APP_DIRS': True,

        'OPTIONS': {
            # Контекстные процессоры добавляют общие данные в шаблоны.
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Путь к WSGI-приложению.
# Используется для запуска проекта WSGI-серверами.
WSGI_APPLICATION = 'django_project_nikolaichyk.wsgi.application'


# Настройки подключения к базе данных.
# Сейчас используется SQLite — база данных хранится в файле db.sqlite3.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Тип базы данных
        'NAME': BASE_DIR / 'db.sqlite3',         # Путь к файлу базы данных
    }
}


# Проверка надёжности паролей пользователей.
# Django будет применять эти правила при установке паролей.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # Пароль не должен быть слишком похож на данные пользователя.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # Проверка минимальной длины пароля.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Запрет распространённых и слишком простых паролей.
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Запрет паролей, состоящих только из цифр.
    },
]


# Настройки языка и времени.
LANGUAGE_CODE = 'en-us'  # Язык интерфейса Django.
TIME_ZONE = 'UTC'        # Часовой пояс проекта.

USE_I18N = True  # Включает поддержку интернационализации.
USE_TZ = True    # Включает поддержку часовых поясов.


# Настройки статических файлов: CSS, JavaScript и изображений.
STATIC_URL = 'static/'


# Настройки отправки электронной почты.
# В консольном режиме письма выводятся в терминал,
# а не отправляются реальному получателю.
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

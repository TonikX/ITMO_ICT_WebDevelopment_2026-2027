# Лабораторная работа №2 — простой сайт на Django

Борисюк Евгений, K3340. Вариант №5 — список научных конференций.

## Состав работы

- Каталог конференций, тематики, место, даты и условия участия.
- Регистрация пользователей и авторов выступлений; изменение и удаление своих регистраций.
- Отзывы с автором, датами конференции и рейтингом 1–10.
- Результаты выступлений через Django-admin и отдельную страницу администратора.
- Таблица участников по конференциям, поиск, фильтрация и пагинация каталога.
- Практики 2.1–2.3: автовладельцы, автомобили, история владения и удостоверения.

## Структура

```text
laboratory_work_2/
├── manage.py
├── django_project_borisuk/  # настройки и маршруты
├── conferences/            # вариант №5, тесты, миграции и seed_demo
├── project_first_app/      # практики: пользователь, автомобили, FBV и CBV
├── jinja2/                 # пользовательские страницы
├── static/style.css        # оформление
├── docs/                   # отчёты, сценарии защиты и скриншоты
├── mkdocs.yml
├── requirements.txt
└── requirements-docs.txt
```

## Требования

Python 3.10, PostgreSQL 14+; версии Python-зависимостей закреплены в requirements.txt.
Проверено с Python 3.10.21, Django 3.2.25, Jinja2 3.1.6,
psycopg2-binary 2.9.11 и PostgreSQL 18.6.
Django 3.2 соответствует указанной в условии ветке Django 3.
Эта версия [больше не поддерживается](https://docs.djangoproject.com/en/3.2/releases/3.2.25/),
поэтому проект предназначен для локальной учебной демонстрации.

Все команды ниже выполняются из каталога laboratory_work_2.

## Установка и PostgreSQL

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

В работающем локальном PostgreSQL создайте отдельную роль и базу, например через psql
с правами администратора PostgreSQL:

```sql
CREATE ROLE web_lab2 LOGIN CREATEDB;
\password web_lab2
CREATE DATABASE web_lab2 OWNER web_lab2;
```

Команда \password запрашивает пароль интерактивно. CREATEDB нужен для временной тестовой базы.
В терминале приложения задайте параметры подключения:

```bash
export PGDATABASE=web_lab2
export PGUSER=web_lab2
export PGHOST=127.0.0.1
export PGPORT=5432
read -rs PGPASSWORD
export PGPASSWORD
```

Введите пароль роли и нажмите Enter. Переменные можно также настроить в конфигурации запуска PyCharm.
Файлы .env автоматически не загружаются. Секреты не добавляются в Git.

## Запуск

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Откройте http://127.0.0.1:8000/. Команда seed_demo повторяемая: добавляет восемь конференций,
двух учебных владельцев и четыре автомобиля. Существующие записи не перезаписывает.
Пароли демонстрационных владельцев отключены; обычного автора создайте через «Регистрация».

Основные страницы:

| Адрес | Назначение | Доступ |
|---|---|---|
| / | Каталог, поиск, тематики, страницы | Все |
| /conferences/1/ | Карточка, своё выступление, отзывы | Все; действия после входа |
| /accounts/signup/ | Создание пользователя | Все |
| /accounts/login/ | Вход | Все |
| /participants/ | Таблица участников и результаты | Администратор |
| /admin/ | Django-admin, конференции, тематики, результаты | По правам Django-admin |
| /practice/owners/ | FBV списка владельцев | Администратор |
| /practice/owner/1 | Карточка пользователя-автовладельца | Администратор |
| /practice/cars/ | CBV списка, карточки и форм автомобилей | Администратор |

Идентификаторы в примерах могут отличаться. Открывайте записи через ссылки в списках.

## Проверка

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --verbosity 2
python -m compileall -q django_project_borisuk conferences project_first_app
python -m mkdocs build --strict
ruff check .
ruff format --check .
git diff --check
```

Тесты создают отдельную базу test_web_lab2 и удаляют её после завершения.
Не запускайте их с настройками рабочей базы реального сервиса.

Версия Ruff закреплена в requirements-dev.txt, правила — в ruff.toml:
E4, E7, E9, F и I (базовые ошибки Python, импорты и неиспользуемые имена).
Команда ruff check . использует именно эту конфигурацию. Форматирование
проверяется отдельно; произвольные расширенные наборы правил не заявляются.

## Документация и защита

[Отчёт ЛР2](docs/lab2/index.md), [практические задания](docs/practice.md).
Подробные разделы: [установка](docs/lab2/setup.md), [модели](docs/lab2/models.md),
[интерфейсы](docs/lab2/interfaces.md), [тестирование и защита](docs/lab2/testing.md).
MkDocs собирает единый сайт с неизменённым текстом отчёта ЛР1 и страницами ЛР2.
Локальный просмотр: `python -m mkdocs serve` (остановите runserver или выберите другой порт).

Приложение рассчитано на локальную учебную демонстрацию. Для публичного размещения
нужны собственный DJANGO_SECRET_KEY, DJANGO_DEBUG=0, разрешённые хосты и настройка HTTPS/static.
`DJANGO_SECRET_KEY` по умолчанию — открытое локальное значение, а не рабочий секрет.

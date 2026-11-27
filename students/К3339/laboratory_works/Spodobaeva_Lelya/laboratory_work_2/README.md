# Лабораторная работа №2

Леля Сподобаева, К3339. Вариант 4 «Список туров туристической фирмы».

На сайте можно зарегистрироваться, найти тур по названию, турагентству или стране, забронировать его и оставить отзыв с оценкой от 1 до 10. В личном кабинете можно редактировать и удалять свои бронирования. После редактирования бронь снова ожидает подтверждения.

Подтверждать бронирования можно на странице «Управление бронями» (`/admin-reservations/`) или через действие «Подтвердить выбранные бронирования» в Django-admin. Страница `/sold-by-country/` показывает проданные туры и итоги по бронированиям и туристам в каждой стране. В отчёт попадают только подтверждённые бронирования.

Шаблоны сайта в `simple_django_web_project/templates/` обрабатывает Jinja2. Django-admin использует Django Templates.

[Отчёт MkDocs со скриншотами](https://lalalalalalalalalalalalalata-del.github.io/ITMO_ICT_WebDevelopment_2026-2027/lr2/report/)

## Подготовка к запуску

Из корня репозитория перейдите в папку лабораторной и установите зависимости. Проверено на Python 3.9.6, Django 4.2.30 и PostgreSQL 18.3.

```bash
cd students/К3339/laboratory_works/Spodobaeva_Lelya/laboratory_work_2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Перед командами Django задайте ключ в текущем терминале. Если ключ уже задан, используйте его прежнее значение, чтобы сохранить действующие сеансы.

```bash
export DJANGO_SECRET_KEY="$(python -c 'from secrets import token_urlsafe; print(token_urlsafe(48))')"
```

Перед первым запуском `seed_data` задайте пароль демонстрационных аккаунтов через скрытый ввод.

```bash
export DEMO_PASSWORD="$(python -c 'from getpass import getpass; print(getpass("Пароль для демо-аккаунтов: "))')"
```

## Запуск на macOS с PostgreSQL

Откройте Postgres.app и запустите сервер. Следующие команды используют локальную роль с именем пользователя macOS. Выполните `createdb` один раз, если базы `tour_agency` ещё нет.

```bash
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
pg_isready -h 127.0.0.1 -p 5432
createdb -h 127.0.0.1 -p 5432 -U "$USER" tour_agency
```

Если имя вашей роли отличается от имени пользователя macOS, укажите его в `createdb -U` и в `POSTGRES_USER`. Если сервер запрашивает пароль, задайте `POSTGRES_PASSWORD` в текущем терминале. Django также использует `~/.pgpass`, если она настроена.

```bash
export USE_POSTGRES=1
export POSTGRES_DB=tour_agency
export POSTGRES_USER="$USER"
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5432

cd simple_django_web_project
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

Откройте [сайт](http://127.0.0.1:8000/) или [Django-admin](http://127.0.0.1:8000/admin/). Для Django-admin и управления бронями можно использовать аккаунт, созданный через `createsuperuser`.

`seed_data` добавляет 12 туров по разным странам, три обычных аккаунта, подтверждённые и ожидающие подтверждения бронирования, а также отзывы со всеми оценками от 1 до 10. Для входа под `tour_demo_anna`, `tour_demo_ivan` или `tour_demo_maria` используйте пароль, который задали при создании аккаунтов. При повторном запуске сохраняются записи, статусы и пароли существующих аккаунтов.

## Запуск с SQLite

Из папки с `manage.py` в активированном виртуальном окружении выполните следующие команды. Django применит миграции к локальному файлу `db.sqlite3`.

```bash
unset USE_POSTGRES
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Проверки и версия Django

Из папки с `manage.py` выполните следующие команды. Для тестов PostgreSQL роли нужно право `CREATEDB`, поскольку Django создаёт отдельную тестовую базу. Для прогона на SQLite выполните `unset USE_POSTGRES`.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test library
```

В методичке в разделе «Цель» указан Django 2.2, а в практическом задании — Django 3. В проекте используется имевшийся Django 4.2.30. Функциональность варианта проверена на 4.2.30. При строгом требовании Django 3 использование 4.2.30 нужно согласовать с преподавателем. [Текст задания](https://drive.google.com/file/d/1kp4xcF-6r-g5jvephy69n9XvS-7hU4KT/view?usp=sharing)

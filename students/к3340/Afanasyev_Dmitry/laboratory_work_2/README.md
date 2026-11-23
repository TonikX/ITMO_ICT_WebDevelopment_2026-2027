# Skyboard — ЛР2, вариант 3 «Табло авиаперелётов»

Автор: Афанасьев Дмитрий, группа К3340.

Django 5.2 LTS, Python 3.10+, Jinja2, PostgreSQL. В задании указан Django 3 / Python 3.6; для совместимости с установленным Python 3.14 проект реализован на Django 5.2. Обсудите версию с преподавателем, если он требует именно Django 3.

## Запуск

Все команды выполняются из этой папки.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/local_postgres.py
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

`local_postgres.py` использует установленный PostgreSQL и создаёт отдельный кластер в `.local/postgres`, порт 55432. Системные базы не изменяются. Остановить его: `python scripts/local_postgres.py stop`.

Альтернатива при наличии Docker: вместо `local_postgres.py` выполните `docker compose up -d --wait`. Для другой базы измените `.env`.

- Сайт: http://127.0.0.1:8000/
- Django-admin: http://127.0.0.1:8000/admin/
- Практики: http://127.0.0.1:8000/practice/owners/ (после входа администратором)
- Локальные демо-пользователи: `admin` и `passenger`, пароль `SkyboardDemo2026!`.

Демо-пароль используется только локально; для него можно задать SKYBOARD_DEMO_PASSWORD. `seed_demo` повторно не удаляет данные и не сбрасывает пароли существующих пользователей.

## Проверка

```sh
python manage.py check
python manage.py test flights project_first_app
python manage.py makemigrations --check --dry-run
mkdocs build --strict
mkdocs serve -a 127.0.0.1:8001
```

В `docs/` лежит полный отчёт, ER-диаграмма, описание интерфейсов, практик и сценарий защиты. Скриншоты сняты с работающего локального приложения.

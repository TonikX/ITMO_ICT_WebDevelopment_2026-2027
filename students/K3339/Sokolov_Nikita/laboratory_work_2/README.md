# Лабораторная работа 2 — Вариант 6: Табло победителей автогонок

Django 4.2 + PostgreSQL.

## Требования

- Python 3.9+
- PostgreSQL

Создать БД `racing_db`. Параметры подключения и демо-пароли задаются в файле `.env` (не коммитится).

```bash
cp .env.example .env
# заполните DJANGO_SECRET_KEY, POSTGRES_*, DEMO_*_PASSWORD
```

## Запуск

```bash
cd students/K3339/Sokolov_Nikita/laboratory_work_2
python3 -m venv .venv
```

Активация venv:
- macOS / Linux: `source .venv/bin/activate`
- Windows: `.venv\Scripts\activate`

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

Учётные записи после `seed_data` — те, что указаны в `.env` (`DEMO_ADMIN_PASSWORD`, `DEMO_USER_PASSWORD`). Логины: `admin`, `racer1`.

## Функционал

- Регистрация и вход
- Список гонок с поиском и пагинацией
- Регистрация на гонку, правка и удаление своей заявки
- Комментарии (тип, рейтинг 1–10, дата заезда)
- Администратор в клиенте: CRUD гонок и результатов
- Таблица участников и результатов
- Панель Django: `/admin/`

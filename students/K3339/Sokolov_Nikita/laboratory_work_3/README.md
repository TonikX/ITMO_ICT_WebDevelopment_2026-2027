# Лабораторная работа 3 — Вариант 10: лечебная клиника

Django 4.2 + DRF + Djoser + PostgreSQL.

## Секреты

```bash
cp .env.example .env
```

Заполните `DJANGO_SECRET_KEY`, `POSTGRES_*`, `DEMO_ADMIN_PASSWORD`.

Создайте БД `clinic_db`.

## Запуск

```bash
cd students/K3339/Sokolov_Nikita/laboratory_work_3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_clinic
python manage.py runserver
```

API: http://127.0.0.1:8000/api/  
Auth (Djoser): http://127.0.0.1:8000/auth/  
Admin: http://127.0.0.1:8000/admin/

После `seed_clinic`: логин `admin`, пароль из `DEMO_ADMIN_PASSWORD`.

## Основные эндпоинты

| Method | URL | Что |
|--------|-----|-----|
| CRUD | `/api/doctors/`, `/api/patients/`, `/api/visits/`, … | сущности клиники |
| GET | `/api/medical-cards/<id>/visits/` | карта + приёмы (1:N nested) |
| GET | `/api/doctors/<id>/patients/` | врач + пациенты через Visit (N:M) |
| POST | `/auth/users/` | регистрация |
| POST | `/auth/token/login/` | токен |
| GET | `/auth/users/me/` | текущий пользователь |
| GET | `/api/analytics/...` | аналитика варианта 10 |

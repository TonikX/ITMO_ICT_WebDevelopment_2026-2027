# Лабораторная работа 2

Код лежит в `students/K3342/laboratory_works/Kornilov_Ivan/laboratory_work_2`.

В папке два проекта Django:

- `django_project_kornilov` — практические работы 2.1, 2.2 и 2.3 (автовладельцы);
- `conference_site` — вариант 5, список научных конференций.

По умолчанию оба проекта используют SQLite: так сайт запускается без отдельного сервера базы. Если нужна PostgreSQL, создайте базу и перед командами задайте переменные `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`. Для PostgreSQL нужен пакет `psycopg`.

## Установка

Из этой папки:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Практики 2.1–2.3. Автовладельцы

```bash
cd django_project_kornilov
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

Страница первого владельца: http://127.0.0.1:8000/owner/1/

Админка: http://127.0.0.1:8000/admin/

| Логин | Пароль | Кто |
| --- | --- | --- |
| admin | admin12345 | суперпользователь, Иван Петров |
| maria | owner12345 | владелец |
| olga | owner12345 | владелец |
| sergey | owner12345 | владелец |
| dmitry | owner12345 | владелец |

Нового владельца можно добавить формой на `/owners/create/`, автомобиль — на `/cars/create/`.

## Вариант 5. Список научных конференций

Сервер практик нужно остановить, если он занимает порт 8000.

```bash
cd conference_site
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

| Логин | Пароль | Кто |
| --- | --- | --- |
| admin | admin12345 | сотрудник оргкомитета, указывает рекомендацию к публикации |
| anna | guest12345 | автор, есть свои доклады и отзыв |
| petr | guest12345 | автор |

Таблица участников: http://127.0.0.1:8000/participants/

Админка: http://127.0.0.1:8000/admin/ — у регистраций на выступление есть действия «Рекомендовать к публикации» и «Не рекомендовать к публикации».

## Просмотр отчёта

Из корня репозитория:

```bash
python3 -m pip install mkdocs mkdocs-material
python3 -m mkdocs serve
```

Отчёт по ЛР2: http://127.0.0.1:8000/laboratory_work_2/report2/

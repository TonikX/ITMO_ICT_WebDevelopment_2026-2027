# ЛР2. Учёт домашних заданий (Django)

Титор Матвей, K3339. Вариант 2 — доска домашних заданий: преподаватель
публикует задания (предмет, преподаватель, дата выдачи, срок выполнения,
текст, штрафы), ученики отправляют решения текстом, отметки выставляются
через Django-admin, есть статистика отметок по группам.

Python 3.10+, Django 4.2, SQLite (или PostgreSQL через переменные окружения),
шаблоны Django, тема Bootswatch Sketchy (Bootstrap 5).

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py fill_data
python manage.py runserver
```

Сайт — http://127.0.0.1:8000/

## Демо-аккаунты (после fill_data)

| Роль | Логин | Пароль |
|------|-------|--------|
| Учитель (staff) | `anna` | `anna12345` |
| Ученик | `oleg` | `pass12345` |
| Ученик | `kate` | `pass12345` |
| Ученик | `dima` | `pass12345` |

Своего суперпользователя можно создать: `python manage.py createsuperuser`.

## Страницы

- `/` — список заданий: фильтр по предмету, поиск, пагинация (7 на страницу)
- `/task/<id>/` — задание: отправка решения, изменение и удаление до проверки
- `/mine/` — мои работы с отметками (только для вошедших)
- `/stats/` — статистика отметок по заданиям и группам
- `/signup/` — регистрация ученика с указанием группы
- `/admin/` — панель администратора (выставление отметок)

## Тесты

```bash
python manage.py test tasks
```

## PostgreSQL (необязательно)

```bash
set DB_ENGINE=postgres
set DB_NAME=lab2& set DB_USER=postgres& set DB_PASSWORD=...
pip install psycopg2-binary
python manage.py migrate
```

## Структура

```
laboratory_work_2/
├── manage.py
├── board/                     проект (settings, urls, wsgi)
├── tasks/                     приложение
│   ├── models.py              Task, Work, StudentProfile
│   ├── views.py               страницы
│   ├── forms.py               регистрация и отправка работы
│   ├── admin.py               админка
│   ├── urls.py
│   ├── tests.py
│   ├── management/commands/fill_data.py
│   ├── templates/tasks/       шаблоны
│   └── static/tasks/style.css
├── practical_works/           практики 2.1–2.3 (Автовладельцы)
└── requirements.txt
```

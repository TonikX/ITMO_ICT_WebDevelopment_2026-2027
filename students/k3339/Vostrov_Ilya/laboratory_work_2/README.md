# ЛР2. "Доска домашних заданий" — сайт на Django

Востров Илья, группа K3339. Вариант 2 — **доска домашних заданий**
(предмет, преподаватель, дата выдачи, период выполнения, текст задания,
информация о штрафах; сдача текстом; отметки через Django-admin;
сводка отметок класса).

Стек: Python 3.9+ · Django 3.2 · БД SQLite по умолчанию (переключение
на PostgreSQL — через переменные окружения) · шаблоны Django (Jinja-подобные)
· Bootstrap 5 через CDN.

## Возможности

- Регистрация пользователей и вход/выход (пароль хранится в защищённом виде).
- Список домашних заданий с **фильтром по предмету**, **поиском** по тексту
  и преподавателю и **пагинацией**.
- Страница задания: сдача решения текстом, просмотр/изменение/удаление своего
  решения (до выставления отметки), отметка "после срока".
- "Мои работы" — сданные решения с отметками (пагинация).
- "Сводка отметок класса" — агрегация по учебной группе; у учителя — выбор
  произвольной группы и таблица по всем классам.
- **Разграничение прав**: ученик (`is_staff=False`) и учитель (`is_staff`/
  `is_superuser`); отметки учитель выставляет в Django-admin
  (`/admin/homework/submission/`).

## Запуск

```bash
# 1. Виртуальное окружение и зависимости
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Миграции (создаёт db.sqlite3)
python manage.py migrate

# 3. (необязательно) демо-данные: учитель/ученики/задания/работы
python manage.py seed_demo

# 4. Запуск
python manage.py runserver
# открыть http://127.0.0.1:8000/
```

Демо-учётные записи после `seed_demo`:

| Роль  | Логин    | Пароль       |
|-------|----------|--------------|
| Учитель | `teacher` | `teacher123` |
| Ученик | `ivan`    | `student123` |
| Ученик | `maria`   | `student123` |
| Ученик | `petr`    | `student123` |

> Учитель — это пользователь с флагами `is_staff`/`is_superuser`. Суперпользователя
> можно также создать штатно: `python manage.py createsuperuser`.

## PostgreSQL (задание рекомендует PostgreSQL)

По умолчанию проект работает на SQLite — это удобно для проверки без установки
СУБД. Для PostgreSQL задайте переменные окружения перед `migrate`/`runserver`:

```bash
export DB_ENGINE=postgres
export DB_NAME=lab2 DB_USER=postgres DB_PASSWORD=secret DB_HOST=127.0.0.1
pip install psycopg2-binary
python manage.py migrate
```

## Тесты

```bash
python manage.py test homework          # 15 тестов
```

Документация — в `docs/`, конфигурация — в `mkdocs.yml`.

## Структура

```
laboratory_work_2/
├── manage.py                 # точка входа Django
├── config/                   # настройки проекта (settings, urls, wsgi, asgi)
├── homework/                 # приложение "Доска домашних заданий"
│   ├── models.py             # Homework, Submission, Profile
│   ├── views.py              # контроллеры
│   ├── forms.py              # регистрация и сдача решения
│   ├── admin.py              # панель администратора (отметки)
│   ├── urls.py               # маршруты приложения
│   ├── tests.py              # тесты (django.test.TestCase)
│   ├── management/commands/seed_demo.py   # демо-данные
│   ├── templates/            # шаблоны (Bootstrap 5)
│   └── static/homework/style.css
├── docs/                     # отчёт MkDocs
├── mkdocs.yml
├── requirements.txt
└── README.md
```

# Практические занятия (ЛР2) — Django

Три самостоятельных Django-проекта на тему «Автовладельцы», каждый запускается
независимо.

| Папка       | Занятие | Содержание |
|-------------|---------|------------|
| `practice1` | 2.1 | Первый проект: модель, миграции, админка, представление `owner()` и маршрут `/owner/<id>/` |
| `practice2` | 2.2 | «Многие ко многим» через `through=Ownership`; FBV (все владельцы) и CBV (List/Detail/Update для автомобилей); формы: FBV-форма владельца, CBV Create/Update/Delete автомобиля |
| `practice3` | 2.3 | Расширение пользователя: `User(AbstractUser)` с полями «номер паспорта / домашний адрес / национальность», `AUTH_USER_MODEL`, вывод в админке и на страницах, форма регистрации с новыми атрибутами |

## Общее

- Стек: Python 3.9+, Django 3.2, SQLite, Bootstrap 5 (шаблоны).
- Единое venv можно переиспользовать: `python3 -m venv .venv && source .venv/bin/activate
  && pip install -r practice1/requirements.txt`.
- В каждой практике: `python manage.py migrate && python manage.py seed_data
  && python manage.py runserver`.

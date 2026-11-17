# Основное задание — вариант 4

Сайт туристической фирмы на Django, Jinja2 и PostgreSQL.

## Запуск

Нужны Python 3.12+ и запущенный PostgreSQL 14+. Команды выполняются из папки `main`.

```fish
source /Users/ilhomsoliev/PycharmProjects/ITMO_ICT_WebDevelopment_2026-2027/.venv/bin/activate.fish
cp .env.example .env
python manage.py migrate
python manage.py seed_tours
python manage.py runserver
```

Если база `itmo_tours` ещё не создана, создай её перед миграциями:

```fish
createdb -h localhost -U postgres itmo_tours
```

В `.env` укажи имя пользователя и пароль PostgreSQL. Примеры настроек находятся в `.env.example`.
Для входа в Django-admin сначала создай администратора командой `python manage.py createsuperuser`.

Сайт: <http://127.0.0.1:8000/>. Админка: <http://127.0.0.1:8000/admin/>.

## Что реализовано

- регистрация и вход пользователей;
- каталог туров с поиском, фильтром по стране и пагинацией;
- создание, изменение и удаление собственных бронирований;
- отзывы с оценкой от 1 до 10;
- подтверждение заявок в интерфейсе сотрудника и в Django-admin;
- таблица подтверждённых продаж по странам.

Отчёт по заданию находится в [папке report](../report/README.md).

# Администратор гостиницы — лабораторная №3, вариант 1

Django 5.2, DRF 3.16, PostgreSQL (psycopg 3), Djoser, python-dotenv и MkDocs.
Реализованы восемь моделей, CRUD, вложенные сериализаторы, заселение/выселение,
сотрудники, историческое расписание уборки, пять аналитических запросов,
квартальный отчёт и сессионная/токенная авторизация.

## Установка и запуск

Из `hotel_api/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Если `.env` отсутствует, создайте его по `.env.example`. Не перезаписывайте
существующий файл. Укажите DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
существующей PostgreSQL. При Docker запустите Docker Desktop и ваш контейнер.
Compose-файл в лабораторной отсутствует; параметры PostgreSQL не изменены.
SECRET_KEY и DEBUG читаются из окружения; по умолчанию сохранён локальный
учебный запуск. Для внешнего размещения задайте собственный секрет и DEBUG=False.

```bash
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

После установки Djoser обязательно выполните `migrate`: это создаёт стандартную
таблицу rest_framework.authtoken. Новых гостиничных миграций не требуется.
Вход в браузере: `/api-auth/login/`, API: `/api/rooms/`, Admin: `/admin/`.
Интерфейс администратора: `/` (номера), `/guests/` (гости), `/check-in/` (заселение).
Вход также доступен через `/admin/login/?next=/`: требуется активный пользователь с `is_staff=True`.
Фронтенд запускается вместе с Django командой `python manage.py runserver`; отдельная сборка не нужна.
Страницы используют существующий REST API через fetch с сессией Django и CSRF-токеном.
Bootstrap 5 загружается через CDN, поэтому для оформления нужен интернет. Необязательные искусственные справочники:
`python manage.py seed_hotel` (без аккаунтов, заселений и уборок).

## Авторизация и права

| Метод | URL | Назначение |
| --- | --- | --- |
| POST | `/auth/users/` | Регистрация: username, email, password |
| POST | `/auth/token/login/` | Получить auth_token: username, password |
| GET | `/auth/users/me/` | Свои id, username, email |
| POST | `/auth/token/logout/` | Удалить токен, ответ 204 |

Заголовок: `Authorization: Token <токен>`. Регистрация не выдаёт is_staff
или is_superuser. Все гостиничные эндпоинты требуют активного is_staff=True,
включая чтение, аналитику и отчёт. Обычный пользователь имеет доступ только
к стандартным возможностям своего аккаунта Djoser.
Сессии Django сохранены, CSRF включён. SessionAuthentication проверяется первой;
без авторизации и при недостаточных правах возвращается 403.

## API

| URL после `/api/` | Методы |
| --- | --- |
| room-types/, floors/, rooms/, guests/, employees/ | GET, POST |
| room-types/\<id\>/, floors/\<id\>/, rooms/\<id\>/, guests/\<id\>/, employees/\<id\>/ | GET, PUT, PATCH, DELETE |
| accommodations/, accommodations/\<id\>/, stays/, stays/\<id\>/ | GET |
| cleaning-schedules/ | GET, POST |
| cleaning-schedules/\<id\>/ | GET, PATCH, DELETE |
| rooms/\<id\>/accommodations/ | GET, вложенные заселения |
| employees/\<id\>/schedule/ | GET, назначения с вложенными этажами |
| check-in/ | POST |
| accommodations/\<id\>/check-out/ | POST |
| employees/\<id\>/dismiss/ | POST |
| analytics/room-guests/ | GET: room_id, date_from, date_to |
| analytics/guests-by-city/ | GET: city |
| analytics/guest-cleaner/ | GET: guest_id, date |
| analytics/available-rooms/ | GET: date_from, date_to |
| analytics/concurrent-guests/ | GET: guest_id |
| reports/quarterly/ | GET: year, quarter |

Заселение принимает room, guests (ID), check_in и planned_check_out.
Проверяются вместимость и пересечения номера/гостей. В транзакции сохраняются
Accommodation со снимком тарифа и Stay для гостей. Выселение принимает
actual_check_out и сохраняет историю. Конец периода — фактический выезд,
если заполнен, иначе плановый. Интервалы `[начало, конец)`.

Квартальный отчёт считает уникальных гостей номера, количество номеров по этажам,
доход каждого номера и общий доход. Ночи обрезаются границами квартала,
сохранённый тариф умножается на ночи один раз за Accommodation, независимо
от числа гостей. Денежные вычисления — Decimal. Включены пустые номера и этажи.
year: 1–9998, quarter: 1–4; оба параметра обязательны.

В Admin Accommodation, Stay, CleaningSchedule, Room, RoomType и Employee доступны
только для просмотра, чтобы исключить обход бизнес-проверок API.
Floor и Guest используют стандартные возможности Admin и ограничения моделей.

## Проверка

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

## MkDocs

Из родительской папки `laboratory_work_3/`:

```bash
hotel_api/.venv/bin/python -m mkdocs serve -a 127.0.0.1:8001
hotel_api/.venv/bin/python -m mkdocs build --strict
```

Документация на русском: [запуск](../docs/index.md), [модели](../docs/database.md),
[CRUD](../docs/api.md), [бизнес-логика](../docs/business_logic.md),
[аналитика](../docs/analytics.md), [отчёт](../docs/quarterly_report.md),
[Djoser](../docs/authentication.md). Полная схема: [database_design.md](../database_design.md).

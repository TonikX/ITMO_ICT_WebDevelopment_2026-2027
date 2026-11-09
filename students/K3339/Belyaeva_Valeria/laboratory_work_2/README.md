# Nordline — ЛР2, вариант 3

Беляева Валерия Андреевна, K3339. «Табло авиаперелётов».

Django 5.2 LTS, PostgreSQL 16, Jinja2. Дизайн ориентирован на Finnair: светлая палитра, синий акцент, крупный поиск, ясное разделение выбора рейса и управления бронированием.

## Быстрый запуск на этом Mac

Двойной щелчок по `start.command`. Сайт откроется на http://127.0.0.1:8002.

Первый запуск создаёт отдельный локальный кластер PostgreSQL на порту 55432, применяет миграции и добавляет демонстрационные данные. Уже существующий PostgreSQL на порту 5432 не используется. Потребуется установленный PostgreSQL 16 (`brew install postgresql@16`).

Учётные записи: `admin` — сотрудник, `traveler` — пассажир. Случайные пароли создаются при первой загрузке демонстрационных данных и сохраняются только в игнорируемом `.runtime/access.txt`. Все пассажиры, номера документов и билеты демонстрационные.

Остановка сайта — Ctrl+C в его окне. Остановка отдельной БД — `stop.command`.

## Ручной запуск с собственной PostgreSQL

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PGHOST=127.0.0.1 PGPORT=5432 PGDATABASE=nordline PGUSER=your_database_user
# При необходимости задайте PGPASSWORD в окружении.
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8002
```

База `nordline` должна существовать. Подключение настраивается переменными `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`. Для публичного размещения нужны отдельные настройки окружения: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, разрешённые хосты и production-сервер. Текущая конфигурация предназначена для локальной защиты лабораторной.

## Возможности

- Поиск по маршруту, коду аэропорта, дате, номеру рейса, авиакомпании, типу и статусу; пагинация.
- Регистрация, вход и выход через POST.
- Бронирование свободного места, изменение и отмена только своих бронирований.
- При изменении брони регистрация и номер билета сбрасываются до повторного подтверждения сотрудником.
- Отзывы с оценкой 1–10, автором и датой рейса.
- Таблица пассажиров с поиском и пагинацией.
- Сотрудник добавляет пассажира, указывает билет и подтверждает регистрацию как на сайте, так и в Django Admin.
- Практики 2.1–2.3: владельцы, автомобили, история владения и удостоверения; FBV/CBV, формы, расширенный пользователь. Адрес `/practice/`, доступ сотруднику.

## Структура

```text
django_project_belyaeva/  настройки, маршруты, Jinja2
flights/                  модели, формы, представления, админка, демоданные
project_first_app/        практики 2.1–2.3
templates/                страницы сайта и практик
static/                   стили и локальная фотография
docs/lr2/                 отчёт и скриншоты
```

## Отчёт

```bash
.venv/bin/mkdocs serve -a 127.0.0.1:8003
.venv/bin/mkdocs build --strict
```

Отчёт: `docs/lr2/report.md`, практики: `docs/lr2/practices.md`. Сборка — `site/` (игнорируется Git).

## Перенос в репозиторий курса

Код приложения переносится в `students/K3339/Belyaeva_Valeria/laboratory_work_2/`. Не переносить `.venv/`, `.runtime/`, `site/`, `__pycache__/` и локальные доступы. Отчёт и скриншоты из `docs/lr2/` добавить в существующий MkDocs-сайт рядом с ЛР1 и включить в его навигацию. Push, публикация отчёта и отправка в систему сдачи выполняются отдельно.

## Источники

- [Задание ЛР2](https://rendex85.github.io/ITMO_ICT_WebDevelopment_Docs/lab2/assignment/).
- [Finnair — визуальный ориентир](https://www.finnair.com/en).
- [Фотография альпийского озера](https://unsplash.com/photos/aerial-photography-of-lake-surrounded-by-trees-and-mountains-during-daytime-eOpewngf68w) — Luca Bravo, Unsplash; файл загружен с images.unsplash.com/photo-1476514525535-07fb3b4ae5f1.
- Шрифт Manrope: Google Fonts (резервный — Arial).

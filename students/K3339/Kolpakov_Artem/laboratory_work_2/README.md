# Лабораторная работа №2

Работа разделена на два независимых Django-сайта:

- `practice_project` — практические задания 2.1–2.3 про автовладельцев;
- `tour_project` — сайт туристической фирмы по варианту 4.

## Установка

Для Django 3.2 используется Python 3.10.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Создайте две базы данных PostgreSQL:

```bash
createdb -U postgres lab2
createdb -U postgres lab2_tours
```

По умолчанию используются следующие параметры подключения:

```text
DB_NAME=имя_базы
DB_USER=имя_пользователя_PostgreSQL
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=5432
```

При необходимости задайте другие значения через переменные окружения.

## Практические задания

```bash
cd practice_project
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

Сайт будет доступен по адресу `http://127.0.0.1:8000/`. По умолчанию он использует базу `lab2`.

## Сайт туристической фирмы

Во втором терминале активируйте то же окружение и выполните:

```bash
cd tour_project
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

Сайт будет доступен по адресу `http://127.0.0.1:8001/`. По умолчанию он использует отдельную базу `lab2_tours`.

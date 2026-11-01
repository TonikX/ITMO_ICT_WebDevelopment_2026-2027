# Лабораторная работа № 2

Сафонова Арина, K3341. Вариант 6 — «Табло победителей автогонок».

## Состав

- `racing_project/`, `races/`, `templates/`, `static/`, `manage.py` — основной сайт.
- `practice/` — задания 2.1–2.3 и сохраненные учебные данные `data.json`.
- `docs/`, `mkdocs.yml` — исходники отчета MkDocs.
- `requirements.txt` — зависимости.

## Подготовка

Нужны Python 3.9 или 3.10 и PostgreSQL. Команды выполняются из корня работы. Виртуальное окружение и база создаются в соседних каталогах.

```bash
python3 -m venv ../lab2_venv
source ../lab2_venv/bin/activate
pip install -r requirements.txt
```

Для macOS с PostgreSQL 16, установленным через Homebrew:

```bash
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
```

Если локальный сервер PostgreSQL еще не настроен, создайте учебный кластер:

```bash
initdb -D ../lab2_postgres -U lab2 --auth=trust --encoding=UTF8 --locale=en_US.UTF-8
pg_ctl -D ../lab2_postgres -l ../lab2_postgres.log -o "-h 127.0.0.1 -p 55432 -k ''" start
createdb -h 127.0.0.1 -p 55432 -U lab2 lab2_racing
createdb -h 127.0.0.1 -p 55432 -U lab2 lab2_practice
```

Локаль `en_US.UTF-8` нужна для поиска русских названий без учета регистра. Эти команды нужны один раз. Для последующего запуска базы используйте только `pg_ctl ... start`.

Настройки проектов по умолчанию используют роль `lab2` и адрес `127.0.0.1:55432`. Для другого сервера задайте `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`; при необходимости имя базы — `PGDATABASE`.

## Основной сайт

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Откройте `http://127.0.0.1:8000/`. Добавьте гонку через `/admin/`, затем создайте обычного пользователя через `/register/` и зарегистрируйте гонщика. Администратор вводит время и результат в Django-admin или на странице гонки.

## Практики

```bash
python practice/manage.py migrate
python practice/manage.py loaddata practice/data.json
python practice/manage.py createsuperuser
python practice/manage.py runserver 127.0.0.1:8001
```

Откройте `http://127.0.0.1:8001/`. Учебные записи загружаются один раз в новую базу. Пароль сохраненных учебных владельцев `owner1`–`owner6`: `OwnerLab2!2026`.

## Отчет

```bash
mkdocs build --strict --site-dir ../lab2_report
```

Откройте `../lab2_report/index.html`. Исходник основного отчета — `docs/index.md`, практик — `docs/practice.md`.

Сайт останавливается сочетанием Ctrl+C. Для остановки учебной базы:

```bash
pg_ctl -D ../lab2_postgres -m fast stop
```

Все действия выполняются локально.

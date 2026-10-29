# ЛР2 — Сайт на Django. Список отелей

Кудрявцев Кирилл Станиславович, К3342, WEB 2.3. Номер 13, вариант 1.

Стек: Python 3.10, Django 3.2.25, Jinja2, PostgreSQL 15.
Каталог номеров, поиск и пагинация, регистрация и вход, собственные бронирования,
отзывы о проживании, заселение и выселение, таблица постояльцев за последние 30 дней.

## Установка и запуск

Команды выполняются в этой папке. Нужны Python 3.10 и PostgreSQL 15+.

```sh
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

В `.env` задайте собственные `SECRET_KEY` и `DB_PASSWORD`. Ключ можно получить так:

```sh
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Для базы можно использовать установленную PostgreSQL либо контейнер из `compose.yml`:

```sh
docker compose up -d --wait
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:9020
```

Если используется существующая PostgreSQL, создайте пустую базу `web_lab2`,
укажите её пользователя, пароль, адрес и порт в `.env`. Код использует PostgreSQL;
переключения на SQLite нет. База должна иметь UTF-8 локаль, например `en_US.UTF-8`,
для поиска русских названий без учёта регистра.

Сайт: http://127.0.0.1:9020/. Админка: http://127.0.0.1:9020/admin/.
Регистрация обычного пользователя доступна на сайте. Суперпользователь также видит
пункты «Заселение» и «Постояльцы». Действия заселения/выселения есть и в Django-admin.

`seed_demo` добавляет 3 отеля и 12 номеров и допускает повторный запуск.
`seed_demo --with-users` дополнительно создаёт вымышленные проживания и аккаунты
`manager`, `guest`; пароли запрашиваются без отображения в терминале.

## Проверки

```sh
python manage.py test -v 2
python manage.py check
python manage.py makemigrations --check --dry-run
```

Для тестов пользователь PostgreSQL должен иметь право `CREATEDB`:
Django создаёт и удаляет отдельную базу `test_web_lab2`.
Проверены формы, права, отзывы, поиск, границы дат и одновременное бронирование.

## Отчёт

Отчёт находится в корневой папке репозитория `docs/lr2/`.
[Опубликованный отчёт](https://kirillja.github.io/ITMO_ICT_WebDevelopment_2026-2027/lr2/report/).
Практики 2.1–2.3 находятся в
`students/K3342/practical_works/Kudryavtsev_Kirill/simple_django_web_project`.

GitHub Pages размещает документацию; сам Django-сайт запускается локально и работает с PostgreSQL.

# Запуск

Вариант 2 — «Библиотека». API использует существующие Django-модели и PostgreSQL. Версии для запуска: Python 3.12, Django 5.2 LTS, DRF 3.16, Djoser 2.3. В исходном проекте использовался Django новее указанного в задании Django 3; зависимости подобраны под актуальный стек и существующую миграцию.

В PowerShell из каталога `lab3`:

```powershell
python -m pip install -r requirements.txt
$env:DB_PASSWORD = 'ваш пароль PostgreSQL'
cd library_project
python manage.py showmigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

По умолчанию подключение: PostgreSQL `127.0.0.1:5432`, пользователь `postgres`, база `library_db`. При необходимости задайте `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`. Если база новая, сначала создайте пустую `library_db`. Если таблицы уже созданы миграциями, повторно создавать их не нужно. Если таблицы импортированы вручную, сначала проверьте соответствие `0001_initial.py` и историю миграций. В фактической схеме `book_author` использует `id` и уникальную пару `(id_book, id_author)`, а поле читателя называется `last_regeq_at`; API сохраняет эти имена.

Локальный API: `http://127.0.0.1:8000/api/`. В `library_project` команда `python manage.py test` запускает тесты на отдельной базе; пользователю PostgreSQL нужно право на её создание.

В другом терминале из `lab3`:

```powershell
python -m mkdocs serve -a 127.0.0.1:8001
```

Документация: `http://127.0.0.1:8001/`. Статическая сборка: `python -m mkdocs build --strict`.

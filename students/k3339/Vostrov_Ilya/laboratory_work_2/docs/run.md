# Запуск и требования

## Требования

- Python 3.9+ (проверено на 3.9),
- Django 3.2 (`requirements.txt`).

Установка зависимостей в виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Миграции и демо-данные

```bash
python manage.py migrate
python manage.py seed_demo          # (необязательно) демо-данные
```

Команда `seed_demo` создаёт учителя, трёх учеников с учебными группами,
девять домашних заданий и шесть сданных работ (часть уже с отметками).
Повторный запуск безопасен — добавляет только недостающие объекты.

## Запуск dev-сервера

```bash
python manage.py runserver
# открыть http://127.0.0.1:8000/
```

## Демо-учётные записи (после seed_demo)

| Роль    | Логин    | Пароль        |
|---------|----------|---------------|
| Учитель | `teacher`  | `teacher123` |
| Ученик  | `ivan`     | `student123` |
| Ученик  | `maria`    | `student123` |
| Ученик  | `petr`     | `student123` |

Учитель отличается от ученика флагами `is_staff`/`is_superuser` — это основа
разграничения прав (см. [Разграничение прав](rights.md)).

## База данных: SQLite или PostgreSQL

По условию стёка рекомендуется PostgreSQL. Чтобы проект можно было запустить
"из коробки", по умолчанию используется **SQLite** (файл `db.sqlite3`).
Для PostgreSQL достаточно задать переменные окружения перед командами:

```bash
export DB_ENGINE=postgres
export DB_NAME=lab2 DB_USER=postgres DB_PASSWORD=secret DB_HOST=127.0.0.1
pip install psycopg2-binary
python manage.py migrate
python manage.py runserver
```

Логика выбора БД — в `config/settings.py`:

```python
if os.environ.get('DB_ENGINE') == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'lab2'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```
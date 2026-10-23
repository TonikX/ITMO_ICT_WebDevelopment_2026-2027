# Homework Board (Lab 2, Variant 2)

## Setup

```
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data   # creates demo users + subjects + homeworks
python manage.py createsuperuser  # your own teacher/admin account
python manage.py runserver
```

Demo accounts created by `seed_demo_data`:
- Student: `alice` / `AlicePass123`
- Student: `bob` / `BobPass123`

## Switching from SQLite to PostgreSQL

The assignment lists PostgreSQL as required software. This project runs on
SQLite by default (zero setup, good for quick local testing), but switching
is a two-step change in `homework_project/settings.py`:

1. Install the PostgreSQL driver:
   ```
   pip install psycopg2-binary
   ```
2. Replace the `DATABASES` setting with:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'homework_board',
           'USER': 'postgres',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```
   (Create the `homework_board` database in PostgreSQL first, then re-run
   `python manage.py migrate`.)

No other code changes are needed — this is the whole point of Django's ORM:
the same models/views work against either database engine.

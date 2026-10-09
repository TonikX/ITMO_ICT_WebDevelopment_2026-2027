# Практическая работа 2.1

## Установка Django. Первое приложение

---

## 1. Установка

```bash
mkdir laboratory_work_2
cd laboratory_work_2
py -m venv tutorial-env
tutorial-env\Scripts\activate.bat
pip install django
django-admin startproject conference_project
cd conference_project
python manage.py startapp conference_app
```

## 2. Настройка settings.py

## 3. Модели

## 4. Миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Admin
```bash
python manage.py createsuperuser
```

## 6. Первое представление

## Результат
* /admin/ — 3 таблицы: Conferences, Topics, Venues

* /conference/1/ — страница конференции
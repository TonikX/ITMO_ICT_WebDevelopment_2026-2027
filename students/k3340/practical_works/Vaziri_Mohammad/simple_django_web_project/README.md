# Практические работы 2.1–2.3: автовладельцы

Проект `django_project_vaziri`, приложение `project_first_app`.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS
pip install -r requirements.txt
python manage.py makemigrations project_first_app
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_owners     # тестовые владельцы, автомобили, владения
python manage.py runserver
```

## Что где

| Практика | Что сделано | Адрес |
|---|---|---|
| 2.1 | Модель Owner, Car, Ownership, DriverLicense; админ-панель; владелец по id | `/admin/`, `/owner/1/` |
| 2.2 | Связь «многие ко многим» Car ↔ Owner через Ownership; список владельцев (FBV); список, детали, создание, изменение и удаление автомобилей (CBV) | `/owners/`, `/cars/`, `/cars/create/`, `/cars/1/update/`, `/cars/1/delete/` |
| 2.2 | Форма ввода владельца (FBV) | `/owners/create/` |
| 2.3 | Owner — пользователь (AbstractUser) с полями номер паспорта, домашний адрес, национальность; поля видны в Django Admin; форма создания пользователя | `/owners/create/`, `/admin/project_first_app/owner/` |

# Практика 2.1–3.1 — Django (автовладельцы = пользователи)

Проект: `django_project_sokolov`
Приложение: `project_first_app`
`AUTH_USER_MODEL = project_first_app.CarOwner`

## Секреты

Скопируйте `.env.example` в `.env` и задайте `DJANGO_SECRET_KEY`. Файл `.env` в git не коммитится.

```bash
cp .env.example .env
```

## Запуск

```bash
cd students/K3339/Sokolov_Nikita/practical_works/simple_django_web_project
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Админка: http://127.0.0.1:8000/admin/

## Практика 3.1

Создание объектов, фильтры и агрегация:

```bash
python manage.py practice_3_1
```

## Страницы

| URL | Что |
|-----|-----|
| `/owners/` | список владельцев-пользователей |
| `/owners/create/` | создать пользователя с паспортом/адресом/национальностью |
| `/owner/<id>/` | карточка владельца |
| `/cars/` | список авто |
| `/cars/<id>/` | авто |
| `/cars/create/` | создать авто |
| `/cars/<id>/update/` | обновить авто |
| `/cars/<id>/delete/` | удалить авто |

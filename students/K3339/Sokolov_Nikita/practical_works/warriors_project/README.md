# Практика 3.2 — Django REST Framework (warriors)

Проект: `warriors_project`
Приложение: `warriors_app`

## Секреты

```bash
cp .env.example .env
```

Задайте `DJANGO_SECRET_KEY`. Файл `.env` в git не коммитится.

## Запуск

```bash
cd students/K3339/Sokolov_Nikita/practical_works/warriors_project
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_warriors
python manage.py runserver
```

## Эндпоинты

| Method | URL | Что |
|--------|-----|-----|
| GET/POST | `/war/skills/` | список / создание скилов (APIView) |
| GET | `/war/warriors/profession/` | воины + профессии |
| GET | `/war/warriors/skill/` | воины + скилы |
| GET | `/war/warriors/<id>/` | воин + профессия + скилы |
| DELETE | `/war/warriors/<id>/delete/` | удаление воина |
| PUT/PATCH | `/war/warriors/<id>/update/` | редактирование воина |

Browsable API: http://127.0.0.1:8000/war/skills/

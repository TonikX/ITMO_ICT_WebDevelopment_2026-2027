# Practice 3.2 — Django REST Framework (warriors)

CRUD for warriors / skills / professions, serializers, generic views and `related_name` / m2m demo.

## Models

- `Skill`
- `Profession` (`related_name="warriors"`)
- `Warrior`
- `SkillOfWarrior` (through + mastery `level`)

## Endpoints

| Method | URL | Purpose |
|--------|-----|---------|
| GET/POST | `/api/warriors/` | list / create |
| GET/PUT/PATCH/DELETE | `/api/warriors/<id>/` | detail |
| GET/POST | `/api/skills/` | skills |
| GET/POST | `/api/professions/` | professions |
| GET | `/api/related-demo/` | `related_name` / m2m examples |

## Run

```bash
cd practice/practice_3_2
python manage.py migrate
python manage.py test
python manage.py runserver 8001
```

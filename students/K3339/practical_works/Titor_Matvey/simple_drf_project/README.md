# Практические работы 3.1 и 3.2 (к ЛР3)

Титор Матвей, K3339. Два Django-проекта на PostgreSQL.

## practice_3_1 — Django ORM (автовладельцы, БД owners_db)

Модели: Owner, Car (M2M на владельцев через Possession), License (OneToOne).
Команда `python manage.py practice` выполняет все задания практики:

- ПЗ1 — создание данных (7 владельцев с удостоверениями, 6 машин, владения);
- ПЗ2 — фильтры и связи (`filter` по марке/имени, `related_name`-связь
  `cars__color`, поиск по году владения `started_at__year`, `distinct`);
- ПЗ3 — агрегации (`aggregate` Min/Max) и группировки (`annotate` + `values`,
  Count по владельцам и маркам, сортировка по дате удостоверения).

Запуск:

```bash
python manage.py migrate
python manage.py practice
```

## practice_3_2 — Django REST Framework (warriors, БД warriors_db)

Модели: Warrior (раса, уровень, FK на профессию, M2M скилов через
SkillOfWarrior с уровнем), Profession, Skill.

Эндпоинты (префикс `/war/`):

| Метод | URL | Что это |
|---|---|---|
| GET/POST | `/war/skills/` | ПЗ: скилы (APIView вручную) |
| GET | `/war/warriors/` | ПЗ: все воины + профессии (`select_related`) |
| GET | `/war/warriors_skills/` | ПЗ: все воины + скилы (`prefetch_related`) |
| GET | `/war/warriors/<id>/` | ПЗ: воин по id с профессией и скилами |
| PATCH/PUT | `/war/warriors/<id>/update/` | ПЗ: редактирование воина |
| DELETE | `/war/warriors/<id>/delete/` | ПЗ: удаление воина |
| GET | `/war/warriors_full/` | роутер DRF (детально, depth-сериализаторы) |

Сериализаторы: `SkillSerializer`/`ProfessionSerializer` (ModelSerializer),
`WarriorSerializer` (классический Serializer вручную), `WarriorModelSerializer`
(вложенные), `WarriorDepthSerializer` (depth=1).

Запуск:

```bash
python manage.py migrate
python manage.py runserver
# пример: POST {"title": "Огненный шар"} на /war/skills/
```

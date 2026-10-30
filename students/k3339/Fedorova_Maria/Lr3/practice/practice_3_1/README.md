# Practice 3.1 — Django ORM (автомобили из практики 2.1)

Продолжение предметной области: автовладелец, автомобиль, владение, водительское удостоверение.

## Models

- `CarOwner` — автовладелец
- `Car` — автомобиль (`related_name="cars"`)
- `Ownership` — владение (`related_name="ownerships"`)
- `DriverLicense` — удостоверение (`related_name="licenses"`)

## Что делает скрипт

Файл `project_first_app/orm_queries.py`:

1. создаёт 7 владельцев и 6 автомобилей;
2. каждому выдаёт удостоверение и 1–3 машины через `Ownership`;
3. фильтры: Toyota, имя «Олег», удостоверение по id владельца, красные машины, владение с 2010;
4. агрегаты: min дата удостоверения, max дата владения Camry, count машин по владельцам и маркам, сортировка по дате выдачи.

## Run

```bash
cd practice/practice_3_1
python manage.py migrate
python manage.py test
python manage.py run_practice_3_1
# или:
python manage.py shell < project_first_app/orm_queries.py
```

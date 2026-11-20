# Основное приложение

## Запуск

Требуются Python 3.10+, PostgreSQL и зависимости из `poultry_farm/requirements.txt`.

```bash
cd poultry_farm
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

В `.env` укажи параметры PostgreSQL. По умолчанию приложение ожидает базу `poultry_farm`, пользователя `postgres`, пароль `postgres` и сервер `127.0.0.1:5432`.

```bash
createdb poultry_farm  # выполнить один раз, если базы ещё нет
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API доступно по адресу `http://127.0.0.1:8000/api/`, панель управления — `http://127.0.0.1:8000/admin/`.

Чтобы запустить документацию, из папки `laboratory_work_3` выполни `python -m mkdocs serve`.

## Модель данных

Приложение `farm` повторяет согласованную схему варианта 7. Модель `FarmUser` хранится в таблице `users` и расширяет Django-пользователя ролью. Остальные модели: `Employee`, `EmploymentContract`, `Workshop`, `Cage`, `Breed`, `Chicken`, `ChickenWeightRecord`, `ChickenCageAssignment`, `EmployeeCageAssignment`, `EggProductionRecord`, `Diet` и `BreedSeasonDiet`.

Назначения кур в клетки и работников на клетки являются временными ассоциативными сущностями. Они хранят даты начала и окончания, поэтому сохраняют историю пересадок и закреплений. `BreedSeasonDiet` хранит выбранную диету каждой породы для каждого сезона.

Основные связи:

- `FarmUser` — необязательная учётная запись работника (`Employee`), один к одному;
- `Employee` — трудовые договоры, один ко многим;
- `Workshop` — клетки, один ко многим;
- `Breed` — куры, записи веса, яйца и диеты по сезонам, один ко многим;
- `Chicken` — записи веса, яйца и история клеток, один ко многим;
- `Employee` — клетки, многие ко многим через `EmployeeCageAssignment`;
- `Chicken` — клетки, многие ко многим во времени через `ChickenCageAssignment`;
- `Breed` — `Diet`, многие ко многим через `BreedSeasonDiet`, где поле `season` характеризует связь.

Для связей используются внешние ключи с `related_name`, а уникальность и простые ограничения дополнительно закреплены ограничениями базы данных. Подробности проверок приведены в разделе [Правила данных](rules.md).

# Laboratory work 3

В этой папке находятся три отдельные части ЛР3:

- `practice_3_1` — запросы Django ORM на моделях из практики 2.1;
- `practice_3_2` — REST API на Django REST Framework для воинов, профессий и умений;
- `poultry_farm` — основное приложение по варианту 7 «Птицефабрика».

Практики 3.1 и 3.2 оставлены без изменений. Основное задание использует отдельные модели, настройки, зависимости и базу PostgreSQL.

## Основное приложение

Инструкции по установке и запуску находятся в `docs/poultry-farm.md`. Из папки основного приложения установи зависимости и запусти миграции:

```bash
cd poultry_farm
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
createdb poultry_farm  # выполнить один раз, если базы ещё нет
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Параметры подключения к PostgreSQL задаются в `poultry_farm/.env`. Документация API и расчётов находится в `docs/`.

## MkDocs

Из этой папки запусти локальную документацию:

```bash
python -m mkdocs serve
```

Сборка сайта:

```bash
python -m mkdocs build
```

## Postman

Коллекцию запросов можно импортировать из `postman/Poultry_Farm_LR3.postman_collection.json`. После импорта выполни запрос **Авторизация → Получить токен**: коллекция сохранит токен и будет добавлять его к API-запросам автоматически. Если фактические ID записей отличаются от `1`, обнови соответствующие переменные `*_id` коллекции.

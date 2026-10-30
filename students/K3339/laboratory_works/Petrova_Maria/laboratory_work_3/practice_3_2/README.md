# Практическая работа 3.2 — Django REST Framework

Цель: изучить сериализацию моделей и обработку запросов через APIView и Generic API Views.
Это отдельный учебный Django-проект с SQLite. Практика 3.1 в `../practical_works/` не используется и не изменяется.

## Структура

```text
practice_3_2/
├── manage.py
├── requirements.txt
├── README.md
├── warriors_project/       # настройки, корневые URL, ASGI и WSGI
└── warriors_app/
    ├── models.py          # четыре модели
    ├── serializers.py     # ModelSerializer и вложенные данные
    ├── views.py           # APIView и Generic API Views
    ├── urls.py
    ├── admin.py
    ├── apps.py
    ├── tests.py
    ├── migrations/
    └── management/commands/seed_warriors.py
```

## Модели и сериализаторы

- `Profession`: название `title` и описание `description`.
- `Skill`: название `title`.
- `Warrior`: `race` (student, developer, teamlead), `name`, `level`, необязательная профессия `profession` и навыки `skill`.
- `SkillOfWarrior`: воин `warrior`, навык `skill` и уровень освоения `level`.

Одна профессия может принадлежать нескольким воинам (ForeignKey). При удалении профессии у воина остаётся NULL.
Воин имеет несколько навыков, а навык может принадлежать нескольким воинам (ManyToManyField через SkillOfWarrior).
Удаление воина или навыка удаляет соответствующие промежуточные записи.
`related_name="warrior_skills"` позволяет получить записи навыков вместе с уровнями.
У всех моделей есть `__str__()`.

Сериализаторы чтения явно вкладывают профессию и навыки; `depth` не используется.
Поле `skill` в ответе содержит записи промежуточной модели:

```json
{"id": 1, "skill": {"id": 1, "title": "Python"}, "level": 1}
```

В этой записи внешний `id` — ID связи, `level` — уровень освоения навыка.
В `WarriorUpdateSerializer` редактируются `race`, `name`, `level`, `profession` (ID или null).
Навыки выводятся для чтения; редактирование вложенных связей отдельным API в задании не предусмотрено.
При PUT передавайте все основные поля; PATCH позволяет передать только изменяемые.

## Установка и запуск на macOS

Из корня репозитория:

```bash
cd students/K3339/laboratory_works/Petrova_Maria/laboratory_work_3/practice_3_2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_warriors
python manage.py runserver
```

Рекомендуется Python 3.12 или новее. Настройки предназначены для локальной учебной работы.
База `db.sqlite3` создаётся внутри этого проекта и не включается в Git.
Команда `seed_warriors` создаёт 4 профессии, 6 навыков, 5 воинов и 15 связей.
У каждого воина 3 навыка с уровнями 1, 2, 3. Повторный запуск не создаёт дубликаты и не перезаписывает существующие записи.
Имена воинов и названия профессий/навыков служат ключами поиска тестовых записей.
После удаления тестового воина команда создаст его снова; после переименования запись будет считаться другой.

## Эндпоинты

| Метод | URL | Результат | Представление |
| --- | --- | --- | --- |
| GET | `/api/skills/` | Все навыки | APIView |
| POST | `/api/skills/create/` | Создать навык | APIView |
| GET | `/api/warriors/professions/` | Воины с вложенными профессиями | ListAPIView |
| GET | `/api/warriors/skills/` | Воины с навыками и уровнями освоения | ListAPIView |
| GET | `/api/warriors/<id>/` | Воин с профессией и навыками | RetrieveAPIView |
| DELETE | `/api/warriors/<id>/delete/` | Удалить воина | DestroyAPIView |
| PUT, PATCH | `/api/warriors/<id>/update/` | Изменить воина | UpdateAPIView |

GET/PUT/PATCH возвращают 200, создание — 201, удаление — 204 без тела ответа.
Некорректные данные возвращают 400, отсутствующий воин — 404.
Списки возвращаются JSON-массивами. Создание воинов через API не входит в задание.

## Примеры запросов

Сначала получите ID воинов и профессий из списков: после удаления или повторного наполнения они могут отличаться.
В примерах предполагается, что воин с ID 1 и профессия с ID 1 существуют.

```bash
curl http://127.0.0.1:8000/api/skills/
curl http://127.0.0.1:8000/api/warriors/professions/
curl http://127.0.0.1:8000/api/warriors/skills/
curl http://127.0.0.1:8000/api/warriors/1/

curl -X POST http://127.0.0.1:8000/api/skills/create/ \
  -H 'Content-Type: application/json' \
  -d '{"title": "Python programming"}'

curl -X PUT http://127.0.0.1:8000/api/warriors/1/update/ \
  -H 'Content-Type: application/json' \
  -d '{"race": "developer", "name": "Мария", "level": 5, "profession": 1}'

curl -X PATCH http://127.0.0.1:8000/api/warriors/1/update/ \
  -H 'Content-Type: application/json' \
  -d '{"level": 6, "profession": null}'

curl -X DELETE http://127.0.0.1:8000/api/warriors/1/delete/
```

Для браузерного интерфейса DRF откройте http://127.0.0.1:8000/api/skills/.
На странице `/api/skills/create/` GET вернёт 405, но браузерный интерфейс покажет форму POST.
На `/api/warriors/1/update/` GET также вернёт 405, а ниже будет форма PUT; PATCH можно отправить через curl.
На `/api/warriors/1/delete/` доступна кнопка DELETE. Регистрация и авторизация для API не требуются.

## Проверки

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Тесты используют отдельную временную базу. Проверяются повторное заполнение и связи моделей,
вложенная сериализация, все заданные методы API, сохранение изменений, NULL-профессия,
ошибки валидации, 404, каскадное удаление связей и HTML-интерфейс DRF.

Перед сдачей вручную проверьте формы DRF, JSON-ответы и изменение данных после POST, PUT, PATCH и DELETE.
Подготовьте объяснение связей в `models.py`, вложенности в `serializers.py` и различий представлений в `views.py`.
Использована [официальная документация Generic API Views](https://www.django-rest-framework.org/api-guide/generic-views/)
и [вложенных сериализаторов](https://www.django-rest-framework.org/api-guide/relations/).

Фактически выполнено: Python 3.14.4, Django 5.2.18, DRF 3.16.1. Миграции применены, `check` без ошибок, `makemigrations --check --dry-run` без изменений, все 14 тестов прошли. Команда заполнения запущена дважды. Проверка HTML выполнена тестовым клиентом; ручная проверка в браузере остаётся перед сдачей.

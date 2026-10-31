# Практические работы 2.1–2.3

Govorov Pavel, K3340. Проект `django_project_govorov`, приложение `project_first_app`.

- 2.1: модели владельца, автомобиля, владения и водительского удостоверения; миграции; Django Admin; страница владельца по id.
- 2.2: список и создание владельцев через функции (FBV); список, просмотр, создание, изменение и удаление автомобилей через классы (CBV).
- 2.3: владелец — пользователь на основе `AbstractUser`, добавлены дата рождения, номер паспорта, домашний адрес и национальность. Поля доступны в админке и форме создания пользователя.

У автомобиля несколько владельцев через `Ownership` с датами начала и окончания; проверяется отсутствие пересечений периодов.

## Запуск

Нужны Python 3.10+ и PostgreSQL 14+. Команды из этой папки:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Создайте базу `car_lab` в PostgreSQL (`createdb -U postgres car_lab` или pgAdmin), настройте `.env`.

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 8001
```

Сайт: <http://127.0.0.1:8001/>. Администратор создаётся командой `createsuperuser`.

Для уже подготовленного окружения из корня репозитория:

```powershell
.\.venv\Scripts\python.exe students/k3340/practical_works/Govorov_Pavel/simple_django_web_project/manage.py runserver 8001
```

В текущей локальной базе есть 6 учебных владельцев, 6 автомобилей, водительские удостоверения и история владения. Первым двум учебным владельцам соответствуют по 3 автомобиля; даты передачи не пересекаются. Все паспортные данные и адреса вымышлены. На новом компьютере добавьте данные через формы сайта и Django Admin. Учебные страницы владельцев и CRUD автомобилей доступны без входа; авторизация требуется для Django Admin.

## Маршруты

| URL | Назначение |
|---|---|
| `/` | Список автомобилей, CBV |
| `/owners/` | Список владельцев, FBV |
| `/owner/1` | Владелец по id, FBV |
| `/owners/create/` | Создание пользователя с дополнительными полями, FBV |
| `/cars/1/` | Автомобиль по id, CBV |
| `/cars/create/` | Создание автомобиля, CBV |
| `/cars/1/edit/` | Изменение автомобиля, CBV |
| `/cars/1/delete/` | Подтверждение удаления, CBV; удаление только POST |
| `/admin/` | Управление всеми моделями |

Проверка: `python manage.py check`.

Отчёт находится в общем MkDocs-сайте: `docs/lr2/practice.md`.

# Практические работы 2.1–2.3

Кудрявцев Кирилл, К3342. Проект `django_project_kudryavtsev`, приложение `project_first_app`.

Python 3.10, Django 3.2.25, PostgreSQL. Модели: пользователь-автовладелец,
автомобиль, владение (M2M through с датами), водительское удостоверение.
Владельцы выводятся и создаются через FBV; автомобили — через ListView, DetailView,
CreateView, UpdateView и DeleteView. Новые поля пользователя видны в форме и админке.

```sh
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

В `.env` укажите собственный SECRET_KEY и реквизиты PostgreSQL. Создайте отдельную
базу `web_practice2`. Если база лабы запущена через Docker, из папки ЛР2 выполните:

```sh
docker compose exec db createdb -U web_lab web_practice2
```

Вернувшись в папку практик:

```sh
python manage.py migrate
python manage.py seed_practice
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:9021
python manage.py test -v 2
```

Страницы: `/` — владельцы, `/owner/1/` — владелец по id, `/cars/` — автомобили,
`/register/` — создание пользователя со всеми дополнительными полями,
`/admin/` — управление моделями. Для добавления и изменения данных войдите как сотрудник.
Все данные команды `seed_practice` вымышленные; начальные владельцы имеют недоступные для входа пароли.

Отчёт: корневой `docs/lr2/practice.md` и
[страница MkDocs](https://kirillja.github.io/ITMO_ICT_WebDevelopment_2026-2027/lr2/practice/).

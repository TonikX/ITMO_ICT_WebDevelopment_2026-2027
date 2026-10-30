# Практическое занятие 1 (ЛР2) — «Автовладельцы»

Титор Матвей, группа K3339. Первый проект на Django: развёртывание, модель
данных, миграции, админка, представление и маршрут.

- Проект: `django_project_titor`
- Приложение: `project_first_app`
- Схема данных: владельцы (`Owner`), автомобили (`Car`), владения (`Ownership` —
  промежуточная модель связи с датами покупки/продажи).

## Что реализовано

1. Модель данных по теме «Автовладельцы»: `Owner` (имя, фамилия, дата рождения),
   `Car` (марка, модель, цвет, гос. номер), `Ownership` (FK-связи + start/end даты,
   `ManyToManyField(through='Ownership')`).
2. Миграции: `makemigrations` / `migrate`.
3. Админка: зарегистрированы все модели; демо-данные — два владельца, четыре
   автомобиля, каждому владельцу ≥3 машин, периоды владения не пересекаются.
4. Представление `owner()` через `get_object_or_404` + шаблон `owner.html`.
5. Маршрут `/owner/<id>/` (файл `urls.py` приложения подключен в проект).

Ожидаемый результат: по адресу http://127.0.0.1:8000/owner/1 видно данные
первого владельца и его автомобили.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data          # демо-данные

python manage.py runserver          # http://127.0.0.1:8000/
```

Админка — http://127.0.0.1:8000/admin/ (суперпользователь создаётся штатно:
`python manage.py createsuperuser`).

## Структура

```
practice1/
├── manage.py
├── django_project_titor/       # проект (settings, urls, wsgi, asgi)
├── project_first_app/          # приложение
│   ├── models.py               # Owner, Car, Ownership
│   ├── admin.py                # регистрация моделей
│   ├── views.py                # owner()
│   ├── urls.py                 # /owner/<id>/
│   ├── templates/              # base.html, owner.html
│   └── management/commands/seed_data.py
└── requirements.txt
```

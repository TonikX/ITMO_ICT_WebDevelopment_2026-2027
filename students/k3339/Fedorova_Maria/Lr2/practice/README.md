# Практики 2.1–2.3

Папка на одном уровне с `backend/` и `frontend/` лабораторной работы №2.

- Проект: `django_project_fedorova`
- Приложение: `project_first_app`
- БД: SQLite (`db.sqlite3`)

## Что сделано

### Практика 2.1

- Модели: `CarOwner`, `Car`, `Ownership` (M2M through), `DriverLicense`
- Миграции, регистрация в admin
- FBV `owner/<id>/` + шаблон `owner.html`

### Практика 2.2

- Список владельцев (FBV)
- Список / деталь / update автомобилей (CBV)
- Форма создания владельца (FBV + ModelForm)
- Create / Update / Delete автомобиля (CBV)

### Практика 2.3

- `CarOwner` = кастомный пользователь (`AbstractUser`)
- Поля: паспорт, адрес, национальность (+ дата рождения)
- Поля видны в Django Admin
- Единая страница входа/регистрации `/auth/`
- Вход админа открывает сайт с расширенным функционалом (не Django-admin)

## Запуск

```bash
source ../../../../../.venv/bin/activate
cd practice
python manage.py migrate
python manage.py seed_practice
python manage.py runserver 8001
```

Открыть: http://127.0.0.1:8001/

Админка: http://127.0.0.1:8001/admin/  
Логин после сида: `admin` / `admin`

Демо-владельцы: `ivanov`, `petrova`, `sidorov` (пароль `secret12`).

## Тесты

```bash
python manage.py test project_first_app
```

## Основные URL

| URL                  | Описание                 |
| -------------------- | ------------------------ |
| `/owners/`           | список владельцев        |
| `/owner/1/`          | карточка владельца       |
| `/owners/create/`    | форма владельца (FBV)    |
| `/auth/`             | вход / регистрация       |
| `/logout/`           | выход                    |
| `/cars/`             | список авто              |
| `/cars/<id>/`        | карточка авто            |
| `/cars/create/`      | создать авто             |
| `/cars/<id>/update/` | изменить авто            |
| `/cars/<id>/delete/` | удалить авто             |

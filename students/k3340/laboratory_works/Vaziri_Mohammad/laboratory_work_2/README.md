# ЛР2. Табло победителей автогонок (вариант 6)

Django-проект `racing_board`, приложение `races`.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS
pip install -r requirements.txt
python manage.py makemigrations races
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_races      # демо-данные: гонки, гонщики, результаты, комментарии
python manage.py runserver
```

По умолчанию используется SQLite. Для PostgreSQL создайте базу `racing_board`, скопируйте `.env.example` в `.env`, укажите пароль и повторите `migrate` и `seed_races`.

Демо-пользователи после `seed_races`: `racer1` … `racer10`, пароль `Gonka-2026`.

## Функциональность по заданию

| Требование | Где |
|---|---|
| Регистрация новых пользователей | `/signup/`, вход `/accounts/login/` |
| Просмотр автогонок и регистрация гонщиков | `/races/`, `/races/<id>/`, `/races/<id>/register/` |
| Редактирование и удаление своих регистраций | `/my/registrations/` |
| Отзывы: дата заезда, текст, тип, рейтинг 1–10, комментатор | форма на странице гонки, `/races/<id>/comment/` |
| Время заезда и результаты задаёт администратор | `/admin/races/heat/` (результаты во вкладке заезда) |
| Таблица всех заездов и результатов гонки | страница гонки `/races/<id>/` |
| Табло участников: ФИО, команда, автомобиль, описание, опыт, класс | страница гонки и `/racers/` |
| Меню, пагинация, поиск | навигация Bootstrap, `/races/?q=`, `/racers/?q=&class=` |

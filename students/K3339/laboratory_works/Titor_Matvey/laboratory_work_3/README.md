# ЛР3. «Биржа труда» — REST API на Django REST Framework

Титор Матвей, K3339. Вариант 11 (модель БД согласована с преподавателем).
Стек: Python 3.10+, Django 4.2, Django REST Framework, Djoser (токен-авторизация),
PostgreSQL. Подробное описание эндпоинтов — в отчёте (docs сайта курса, раздел ЛР3).

## Запуск

Нужен запущенный PostgreSQL. По умолчанию настройки: база `labour_exchange`,
пользователь `postgres`, пароль `postgres`, хост `127.0.0.1:5432`
(переопределяется переменными DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT).

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# создать базу (если ещё нет):
# psql -h localhost -U postgres -c "CREATE DATABASE labour_exchange;"

python manage.py migrate
python manage.py fill_data
python manage.py runserver
```

API — http://127.0.0.1:8000/api/v1/ , админка — /admin/ (admin / admin12345).

## Эндпоинты

Djoser: `users/register/`, `users/me/`, `token/login/`, `token/logout/`.

CRUD (router): `professions/`, `applicants/`, `work-experiences/`, `employers/`,
`vacancies/`, `benefits/`, `courses/`, `enrollments/`, `vacancy-matches/`.

Специальные запросы из задания:

| Запрос | Эндпоинт |
|---|---|
| Все варианты вакансий для соискателя (подбор) | `GET /applicants/{id}/matching_vacancies/` |
| Выплачиваемые сейчас пособия | `GET /benefits/active/` |
| Незакрытые вакансии и дней с подачи | `GET /vacancies/unclosed_days/` |
| Профессии, не представленные в вакансиях | `GET /professions/unrepresented/` |
| Вакансии: высшее образование, ЗП 5000–60000 | `GET /vacancies/premium/` |
| Отчёт: открытые вакансии по работодателям | `GET /employers/` (поле `open_vacancies_count`) |

Чтение — всем, запись — только с токеном (заголовок `Authorization: Token <token>`).

## Тесты

```bash
python manage.py test exchange
```

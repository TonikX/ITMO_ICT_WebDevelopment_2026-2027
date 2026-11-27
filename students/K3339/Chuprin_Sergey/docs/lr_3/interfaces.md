# Интерфейсы API

## Запуск

Для запуска нужны Python 3.12 и доступная база PostgreSQL. Из корня репозитория перейдите в папку работы и установите зависимости в виртуальное окружение.

```bash
cd students/K3339/Chuprin_Sergey/lr_3
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install 'Django>=5.2,<7' djangorestframework djoser 'psycopg[binary]' python-dotenv
```

Создайте пустую базу `library` и пользователя PostgreSQL с правами на создание таблиц в ней. Сохраните параметры подключения в файле `.env` рядом с `manage.py`. Имя пользователя и пароль в примере замените своими.

```dotenv
DB_NAME=library
DB_USER=library_user
DB_PASSWORD=your_local_password
DB_HOST=localhost
DB_PORT=5432
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Административный интерфейс Django доступен по адресу `http://127.0.0.1:8000/admin/`. Аккаунт, созданный командой `createsuperuser`, подходит для проверки библиотечного API.

## Авторизация

| Метод | URL | Входные данные и результат |
|---|---|---|
| POST | `/auth/users/` | `username`, `password`. Создаёт обычный аккаунт, возвращает профиль и статус 201. |
| POST | `/auth/token/login/` | `username`, `password`. Возвращает `auth_token` и статус 200. |
| GET | `/auth/users/me/` | Заголовок с токеном. Возвращает профиль текущего пользователя. |
| POST | `/auth/token/logout/` | Заголовок с токеном. Удаляет текущий токен и возвращает статус 204. |

Для обращения к библиотечному API передаётся заголовок `Authorization: Token <токен>`. Доступ к операциям под `/api/` требует аккаунта с признаком `is_staff`. Запрос без токена получает статус 401, а запрос с токеном обычного пользователя — 403. Для JSON-тела указывается `Content-Type: application/json`.

`GET /api/` возвращает ссылки на коллекции. Методы для работы с каталогом, читателями и выдачами приведены ниже.

## Каталог и справочники

Для каждого ресурса в таблице действуют одни и те же методы. `GET` по пути коллекции возвращает список, `POST` создаёт запись со статусом 201. По пути с `{id}/` доступны просмотр (`GET`), полное обновление (`PUT`), частичное обновление (`PATCH`) и удаление (`DELETE`, при успехе 204). `{id}` обозначает идентификатор объекта.

| Коллекция | Поля для записи |
|---|---|
| `/api/authors/` | `name` |
| `/api/publishers/` | `name`, `description` |
| `/api/categories/` | `name` |
| `/api/books/` | `name`, `publisher` (ID), `year_of_publication`, `code`, `category` и `authors` (массивы ID) |
| `/api/rooms/` | `name`, `number`, `capacity` |

В ответе на `GET /api/books/{id}/` поле `authors` содержит объекты авторов. В ответе на `GET /api/publishers/{id}/` поле `books` содержит записи каталога этого издательства.

## Читатели

| Метод | URL | Входные данные и результат |
|---|---|---|
| GET | `/api/readers/`, `/api/readers/{id}/` | Список читателей или карточка выбранного читателя. |
| PUT, PATCH | `/api/readers/{id}/` | Обновляет анкету. Номер билета и дата последней регистрации доступны только для чтения в этих операциях. |
| POST | `/api/readers/register/` | Анкета, `library_card_number` и `reader_room` (ID зала). Создаёт читателя с действующим закреплением, возвращает карточку и статус 201. |
| POST | `/api/readers/{id}/unregister/` | Пустое тело. Закрывает действующее закрепление и возвращает сообщение. |
| POST | `/api/readers/{id}/enroll/` | `reader_room` (ID). Записывает ранее выписанного читателя и возвращает его карточку. |
| POST | `/api/readers/{id}/transfer/` | `reader_room` (ID нового зала). Возвращает новую запись истории закрепления. |
| POST | `/api/readers/{id}/reregister/` | Необязательный `library_card_number`. Обновляет дату последней регистрации, при передаче номера меняет билет, возвращает карточку. |
| POST | `/api/readers/expel-expired/` | Пустое тело. Выписывает читателей, чья последняя регистрация была более года назад. Возвращает `expelled_count`. |
| GET | `/api/readers/{id}/books/` | Книги на руках у читателя. |

Поля анкеты — `name`, `passport_series`, `passport_number`, `date_of_birth`, `address`, `phone_number`, `education` и необязательное `has_academic_degree` (по умолчанию `false`). Дата передаётся в формате `YYYY-MM-DD`. Допустимые значения `education` — `primary`, `secondary`, `higher`. В поле `last_registration_date` сервер записывает дату самостоятельно.

## Экземпляры, выдачи и история

| Метод | URL | Входные данные и результат |
|---|---|---|
| GET | `/api/book-copies/`, `/api/book-copies/{id}/` | Список экземпляров или карточка экземпляра. |
| POST | `/api/book-copies/accept/` | `book` и `reader_room` (ID). Принимает экземпляр в фонд, возвращает его карточку и статус 201. |
| POST | `/api/book-copies/{id}/transfer/` | `reader_room` (ID нового зала). Возвращает новую запись истории закрепления. |
| POST | `/api/book-copies/{id}/scrap/` | Пустое тело. Списывает экземпляр, закрывает его закрепление и возвращает карточку экземпляра. |
| GET | `/api/loans/`, `/api/loans/{id}/` | Список выдач или карточка выдачи. |
| POST | `/api/loans/issue/` | `reader` и `book_copy` (ID). Возвращает карточку новой выдачи и статус 201. |
| POST | `/api/loans/{id}/return/` | Пустое тело. Устанавливает дату возврата и возвращает карточку выдачи. |
| GET | `/api/reader-room-history/`, `/api/reader-room-history/{id}/` | История закрепления читателей за залами или отдельная запись. |
| GET | `/api/book-copy-room-history/`, `/api/book-copy-room-history/{id}/` | История закрепления экземпляров за залами или отдельная запись. |

## Аналитика и отчёт

| Метод | URL | Результат |
|---|---|---|
| GET | `/api/analytics/overdue-readers/` | Читатели с просроченными выдачами. |
| GET | `/api/analytics/rare-book-readers/` | Читатели с открытыми выдачами редких книг. |
| GET | `/api/analytics/young-readers/` | Количество читателей младше 20 лет в поле `count`. |
| GET | `/api/analytics/education/` | `total_readers` и доли в процентах в полях `primary`, `secondary`, `higher` и `academic_degree`. |
| GET | `/api/reports/monthly/?year=2026&month=10` | Отчёт за указанный месяц. Параметры `year` и `month` обязательны. |

В аналитических списках читателей возвращаются только `id`, `name` и `library_card_number`. В месячном отчёте `daily_statistics` содержит даты, общие значения `total_books` и `total_readers` и массив `rooms` с полями `books_count` и `readers_count` по залам. Объект `new_readers` содержит общий итог `total` и массив `rooms` с полем `count` по залам. Каждый зал в отчёте описан полями `room_id`, `room_number` и `room_name`.

Ошибки валидации полей и отказы сервиса, например повторная выдача занятого экземпляра, дают статус 400. Запрос карточки по отсутствующему идентификатору даёт 404. Успешные операции без отдельно указанного статуса возвращают 200.

## Пример выдачи и возврата

Получите токен сотрудника. Замените `staff` и `YOUR_PASSWORD` данными созданного аккаунта.

```bash
API=http://127.0.0.1:8000
curl -sS "$API/auth/token/login/" \
  -H 'Content-Type: application/json' \
  -d '{"username":"staff","password":"YOUR_PASSWORD"}'
```

Скопируйте значение `auth_token` в переменную `TOKEN`. В примере читатель с ID 1 уже записан в зал, а экземпляр с ID 3 принят в фонд и свободен. Эти записи можно подготовить через `/api/readers/register/` и `/api/book-copies/accept/`, предварительно создав зал и запись книги в каталоге.

```bash
TOKEN='YOUR_TOKEN'
curl -sS "$API/api/loans/issue/" \
  -H "Authorization: Token $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"reader":1,"book_copy":3}'
```

Ответ со статусом 201 содержит `id`, `reader`, `book_copy`, `issued_date` и `return_date`. До возврата `return_date` равно `null`. Для возврата подставьте полученный `id` выдачи вместо 7.

```bash
curl -sS -X POST "$API/api/loans/7/return/" \
  -H "Authorization: Token $TOKEN"
```

В ответе поле `return_date` содержит дату возврата.

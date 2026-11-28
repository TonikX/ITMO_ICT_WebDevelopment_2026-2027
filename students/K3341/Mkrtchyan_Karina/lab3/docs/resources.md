# CRUD и вложенные объекты

Все пути ниже начинаются с `/api/`. Для каждого ресурса `GET /api/{resource}/` возвращает список, `POST` создаёт запись (`201`). По пути `/api/{resource}/{id}/` доступны `GET`, `PUT` (полная замена), `PATCH` (частичное изменение) и `DELETE` (`204`). Неизвестный ID — `404`, ошибка полей — `400`, конфликт удаления или записей в базе — `409`. Без токена — `401`, без необходимых прав — `403`.

| Ресурс | ID в ответе | Поля записи |
|---|---|---|
| `authors` | `id_author` | `full_name` |
| `publishers` | `id_publisher` | `name` |
| `sections` | `id_section` | `name` |
| `reading-rooms` | `id_room` | `room_number`, `name`, `capacity` (> 0) |
| `books` | `id_book` | `title`, `publisher`, `section`, `publication_year` (1400–2100), `author_ids` (необязательный список) |
| `book-authors` | `id` | `book`, `author` (пара уникальна) |
| `book-ciphers` | `id_cipher_hist` | `book`, `cipher`, `valid_from`, `valid_to` |
| `copies` | `id_copy` | `book`, `inventory_no`, `acquired_at`, `status` (`ACTIVE` по умолчанию, `WRITTEN_OFF`, `LOST`) |
| `copy-rooms` | `id_location` | `copy`, `room`, `valid_from`, `valid_to` (дата и время) |
| `readers` | `id_reader` | `passport_no`, `full_name`, `birth_date`, `address`, `phone`, `education`, `has_degree`, `registered_at`, `last_regeq_at`, `deregistered_at` |
| `reader-tickets` | `id_ticket_hist` | `reader`, `ticket_no`, `valid_from`, `valid_to` |
| `reader-rooms` | `id_reader_room` | `reader`, `room`, `valid_from`, `valid_to` |
| `loans` | `id_loan` | `copy`, `reader`, `issued_at`, `due_at`, `returned_at` (дата и время) |

Каталог читают все пользователи с токеном; изменяют только сотрудники (`is_staff`). `readers`, `reader-tickets`, `reader-rooms`, `loans` доступны только сотрудникам даже для чтения.

Связи передаются числовыми ID. Даты — `YYYY-MM-DD`, дата и время — ISO 8601, например `2026-07-01T10:00:00Z`. `valid_to`, `returned_at`, `phone`, `deregistered_at` можно не передавать или установить в `null`. При создании читателя `last_regeq_at` по умолчанию равна `registered_at`, `has_degree` — `false`. `education`: `PRIMARY`, `SECONDARY`, `VOCATIONAL`, `HIGHER`, `OTHER`.

## Примеры

`POST /api/books/` (предварительно создайте издателя, раздел и автора):

```json
{"title":"Мастер и Маргарита","publisher":1,"section":1,"publication_year":1967,"author_ids":[1]}
```

`GET /api/books/1/` возвращает вложенные `authors` (многие ко многим) и `copies` (один ко многим):

```json
{"id_book":1,"title":"Мастер и Маргарита","publisher":1,"section":1,"publication_year":1967,"authors":[{"id_author":1,"full_name":"Михаил Булгаков"}],"copies":[{"id_copy":1,"book":1,"inventory_no":"INV-001","acquired_at":"2026-07-01","status":"ACTIVE"}]}
```

`GET /api/books/` также содержит вложенных авторов. `PATCH /api/books/1/` с `{"author_ids":[]}` удаляет все связи; отсутствие поля оставляет их без изменений.

Выдача: `POST /api/loans/` с `{"copy":1,"reader":1,"issued_at":"2026-07-01T10:00:00Z","due_at":"2026-07-15T10:00:00Z"}`. Возврат — `PATCH /api/loans/1/` с `{"returned_at":"2026-07-08T12:00:00Z"}`. API не допускает пересекающихся выдач одного экземпляра.

Перемещение: `POST /api/copy-rooms/` с `{"copy":1,"room":2,"valid_from":"2026-07-01T10:00:00Z"}`. Добавление более поздней записи закрывает предыдущий открытый период. Для историй интервалы полуоткрытые: начало включается, конец — нет.

## Операции библиотекаря

- **Запись читателя:** `POST /api/readers/`, затем `POST /api/reader-tickets/` с `reader`, `ticket_no`, `valid_from` и `POST /api/reader-rooms/` с `reader`, `room`, `valid_from`.
- **Перерегистрация:** обновите `last_regeq_at` через `PATCH /api/readers/{id}/` и создайте запись с новым номером билета. Перевод в другой зал — новая запись `reader-rooms`; переклассификация книги — новая запись `book-ciphers`.
- **Снятие с учёта:** `PATCH /api/readers/{id}/` с датой `deregistered_at`. `POST /api/readers/deregister-expired/` без тела снимает с учёта тех, кто записался и последний раз перерегистрировался строго раньше даты год назад. Ответ `200`: `deregistered_count`, `deregistered_at`. Записи и история сохраняются.
- **Приём в фонд:** при необходимости создайте издание через `POST /api/books/`; добавьте физический экземпляр через `POST /api/copies/` и назначьте зал через `POST /api/copy-rooms/`.
- **Утрата и списание:** `PATCH /api/copies/{id}/` с `{"status":"LOST"}` или `{"status":"WRITTEN_OFF"}`. Если экземпляр убыл из зала, закройте действующее размещение, указав `valid_to` через `PATCH /api/copy-rooms/{id}/`. Это сохраняет прошлое размещение для месячного отчёта.

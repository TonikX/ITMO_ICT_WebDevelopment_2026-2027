# Авторизация Djoser

| Метод и путь | Тело или результат |
|---|---|
| `POST /auth/users/` | `username`, `password`, `email` (необязательно); `201` |
| `POST /auth/token/login/` | `username`, `password` → `200`, `{"auth_token":"..."}` |
| `GET /auth/users/me/` | Текущий пользователь: `id`, `username`, `email` |
| `POST /auth/token/logout/` | Удалить текущий токен; `204` |

Передавайте `Authorization: Token <auth_token>` при запросах к `/api/`, `/auth/users/me/` и при выходе. Для JSON используйте `Content-Type: application/json`.

Обычная регистрация не даёт прав сотрудника. Для демонстрации полного CRUD войдите под пользователем, созданным через `createsuperuser`. Учётная запись Django и запись `Reader` в библиотеке независимы.

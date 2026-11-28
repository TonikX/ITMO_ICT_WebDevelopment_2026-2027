# Авторизация Djoser

| Метод и путь | Тело или результат |
|---|---|
| `POST /auth/users/` | `username`, `password`, `email` (необязательно); `201` |
| `POST /auth/token/login/` | `username`, `password` → `200`, `{"auth_token":"..."}` |
| `GET /auth/users/me/` | Текущий пользователь: `id`, `username`, `email` |
| `POST /auth/token/logout/` | Удалить текущий токен; `204` |

Передавайте `Authorization: Token <auth_token>` при запросах к `/api/`, `/auth/users/me/` и при выходе. Для JSON используйте `Content-Type: application/json`.

Обычная регистрация не даёт прав сотрудника. Для демонстрации полного CRUD войдите под пользователем, созданным через `createsuperuser`. Учётная запись Django и запись `Reader` в библиотеке независимы.

## Проверка в Swagger UI

На запущенном сервере откройте `http://127.0.0.1:8000/api/swagger/`. В `POST /auth/token/login/` нажмите **Try it out**, введите JSON с `username` и `password`, затем нажмите **Execute**. Скопируйте значение `auth_token` и вставьте его в **Authorize** в виде `Token <auth_token>`. Теперь можно запускать защищённые запросы из браузера, например `GET /api/reports/rare-book-loans/` или `POST /api/readers/`.

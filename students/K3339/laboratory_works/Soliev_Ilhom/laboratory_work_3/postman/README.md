# Postman collection

Import `Poultry_Farm_LR3.postman_collection.json` into Postman. The collection variable `base_url` defaults to `http://127.0.0.1:8000`. Run **Авторизация → Получить токен** first; its test script saves `auth_token` as `token`, which is sent automatically as `Authorization: Token {{token}}`.

CRUD requests use `{{..._id}}` variables, initially set to `1`; change them to IDs returned by your API. Create parent records before dependent records. Employee and employment changes require a director or superuser.

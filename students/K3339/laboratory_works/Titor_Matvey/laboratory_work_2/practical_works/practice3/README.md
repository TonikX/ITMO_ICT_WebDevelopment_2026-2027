# Практическое занятие 3 (ЛР2) — «Автовладельцы»

Титор Матвей, группа K3339. Тема — **расширение стандартного пользователя
Django**: владелец автомобиля становится пользователем через `AbstractUser`.

## Что реализовано

1. **Модель `User(AbstractUser)`** в `project_first_app/models.py` с полями:
   - `passport_number` — номер паспорта;
   - `home_address` — домашний адрес;
   - `nationality` — национальность.

2. **Подключение в настройках** (`django_project_titor/settings.py`):
   ```python
   AUTH_USER_MODEL = 'project_first_app.User'
   ```

3. **Другие сущности ссылаются на пользователя** через `settings.AUTH_USER_MODEL`
   (а не на жёстко вшитую модель): поле `Ownership.owner =
   models.ForeignKey(settings.AUTH_USER_MODEL, ...)`.

4. **Django Admin** — собственный `UserAdmin` (`CustomUserAdmin`): дополнительные
   поля видны и редактируемы (в `fieldsets`, `add_fieldsets`, `list_display`,
   `search_fields`). Стандартная регистрация переопределяется через
   `unregister`/`register`.

5. **Вывод расширенных данных в прежнем коде**: страница `/` (список
   пользователей-владельцев) и `/owner/<id>/` показывают номер паспорта,
   домашний адрес и национальность.

6. **Форма создания учётной записи с новыми атрибутами** — `UserRegisterForm`
   (`UserCreationForm` + поля паспорта/адреса/национальности), вьюха `register`
   и страница `/register/`.

## Запуск

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate            # AUTH_USER_MODEL задан до миграций
python manage.py seed_data          # admin + 2 владельца с паспортами + авто

python manage.py runserver          # http://127.0.0.1:8000/
```

Демо-учётные записи (после `seed_data`):

| Роль    | Логин  | Пароль    | Паспорт      |
|---------|--------|-----------|--------------|
| Админ   | admin  | admin123  | 0000 000001  |
| Владелец | ivan  | ivan123   | 4015 123456  |
| Владелец | maria | maria123  | 4019 654321  |

## Маршруты

| URL            | Назначение |
|----------------|------------|
| `/`            | список пользователей-владельцев с паспортом/адресом/национальностью |
| `/owner/<pk>/` | страница владельца и его автомобилей |
| `/register/`   | форма создания учётной записи с новыми атрибутами |
| `/cars/`       | список автомобилей (CBV) |
| `/accounts/login/`, `/accounts/logout/` | вход/выход (штатные Django) |
| `/admin/`      | админка с расширенным UserAdmin |

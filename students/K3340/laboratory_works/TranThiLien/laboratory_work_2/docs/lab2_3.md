# Практическая работа 2.3

## Аутентификация. Admin actions

---

## 1. settings.py

```python
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL           = '/accounts/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```
## 2. URL auth

Django предоставляет:
* /accounts/login/
* /accounts/logout/
* /accounts/password_change/

## 3. Форма регистрации

## 4. View регистрации

## 5. Admin actions

## 6. Таблица участников

## Результат
* /register/ — регистрация с авто-входом

* /accounts/login/ — вход

* /admin/ — 6 таблиц + actions

* /participants/ — сводная таблица
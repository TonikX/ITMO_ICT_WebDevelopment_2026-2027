# Запуск и сдача

## Локальный запуск

Из корня форка:

```bash
cd students/K3339/Danilevskiy_Timur/laboratory_work_2
bash run.command
```

Перед этим запустите Docker Desktop. Требуется Python 3.10. Подробный ручной запуск приведён
в `README.md` рядом с `manage.py`.

| Компонент | Адрес |
|---|---|
| Django-приложение | `http://127.0.0.1:8000/` |
| Django-admin | `http://127.0.0.1:8000/admin/` |
| PostgreSQL | `127.0.0.1:54329`, БД `apex` |
| MkDocs при локальном запуске | `http://127.0.0.1:8001/` |

Для демонстрации создаются локальные аккаунты:

| Роль | Логин | Пароль |
|---|---|---|
| Гонщик | `racer` | `DemoRace2026!` |
| Судья | `judge` | `DemoControl2026!` |

Новый аккаунт можно создать через интерфейс. Демо-данные идемпотентны и служат только для
локальной защиты. Для новых открытых гонок даты задаются относительно первого запуска seed-команды.

## Проверка

Из папки приложения, после активации виртуального окружения:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test tests --verbosity 2
```

Из корня репозитория:

```bash
pip install -r requirements-docs.txt
mkdocs build --strict
mkdocs serve --dev-addr 127.0.0.1:8001
```

## Публикация отчёта

Из корня форка:

```bash
mkdocs gh-deploy
```

MkDocs собирает `docs/` и публикует статический результат в ветку `gh-pages`.
В Settings → Pages следует выбрать **Deploy from a branch**, ветку **gh-pages** и каталог **/ (root)**.
Адрес отчёта: [K1ll4a.github.io/ITMO_ICT_WebDevelopment_2026-2027](https://K1ll4a.github.io/ITMO_ICT_WebDevelopment_2026-2027/).

На GitHub Pages публикуется только отчёт. Django требует Python-сервера и PostgreSQL, поэтому
для защиты запускается локально.

## Pull request

Рабочая ветка: `lab2-k3339-danilevskiy`.
Форк: [K1ll4a/ITMO_ICT_WebDevelopment_2026-2027](https://github.com/K1ll4a/ITMO_ICT_WebDevelopment_2026-2027).
Базовый репозиторий: [TonikX/ITMO_ICT_WebDevelopment_2026-2027](https://github.com/TonikX/ITMO_ICT_WebDevelopment_2026-2027).

Заголовок по формату сдачи: **K3339 Danilevskiy_Timur ЛР2**.

В коммит включаются исходники, миграции, конфигурация MkDocs, Markdown-отчёт и скриншоты.
Виртуальные окружения, `.env`, локальные БД, кэш, `site/` и `staticfiles/` исключены через `.gitignore`.

После исправлений достаточно нового коммита и `git push`: существующий pull request обновляется.

## Порядок показа на защите

1. Открыть главную и календарь, показать поиск и вторую страницу.
2. Открыть завершённую гонку и её протокол с несколькими попытками.
3. Зарегистрировать новый аккаунт и подать заявку на открытую гонку.
4. Изменить номер, показать ошибку занятого номера, отменить заявку.
5. Добавить комментарий с типом, датами и оценкой.
6. Войти как судья, показать Race control, добавить и изменить результат.
7. Продемонстрировать тот же результат в Django-admin и клиентском протоколе.
8. Объяснить связи моделей и серверные проверки доступа.

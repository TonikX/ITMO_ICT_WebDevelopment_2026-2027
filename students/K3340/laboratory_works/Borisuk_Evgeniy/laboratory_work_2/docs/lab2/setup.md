# Установка и запуск

## Окружение

Работа использует Python 3.10, Django 3.2.25, PostgreSQL и Jinja2.
Python 3.14 для этой версии Django не используется. Настройки сайта находятся
в django_project_borisuk/settings.py, зависимости — в requirements.txt.

Откройте каталог laboratory_work_2 в терминале или PyCharm. При открытии всего
репозитория перейдите в каталог работы:

```bash
cd students/K3340/laboratory_works/Borisuk_Evgeniy/laboratory_work_2
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python --version
python -m django --version
```

requirements-dev.txt включает зависимости приложения, MkDocs и Ruff.
Для запуска без средств проверки достаточно requirements.txt.
Если Python 3.10 отсутствует, его необходимо установить отдельно; системный
интерпретатор заменять не требуется.

## Подготовка PostgreSQL

PostgreSQL должен быть установлен и запущен отдельно. Откройте psql с правами
администратора БД и создайте учебную роль:

```sql
CREATE ROLE web_lab2 LOGIN CREATEDB;
\password web_lab2
CREATE DATABASE web_lab2 OWNER web_lab2;
```

Пароль задаётся интерактивно. CREATEDB нужен для создания временной базы тестов,
а не для обычной работы сайта. Используется отдельная учебная роль, не роль
администратора реального сервиса.

В терминале с активным окружением задайте подключение:

```bash
export PGDATABASE=web_lab2
export PGUSER=web_lab2
export PGHOST=127.0.0.1
export PGPORT=5432
read -rs PGPASSWORD
export PGPASSWORD
```

После команды read введите пароль и нажмите Enter. Приложение читает переменные
окружения напрямую. Файлы .env автоматически не загружаются.
Параметры можно также задать через настройки запуска PyCharm.

| Переменная | Назначение | Значение по умолчанию |
|---|---|---|
| PGDATABASE | Учебная база | web_lab2 |
| PGUSER | Роль PostgreSQL | Имя пользователя ОС, затем postgres |
| PGPASSWORD | Пароль роли | Пустая строка |
| PGHOST | Хост или каталог Unix-сокета | localhost |
| PGPORT | Порт | 5432 |
| DJANGO_DEBUG | Подробные локальные ошибки | 1 |
| DJANGO_ALLOWED_HOSTS | Хосты через запятую | localhost, 127.0.0.1, [::1] |
| DJANGO_SECRET_KEY | Ключ Django | Открытое локальное значение |

При использовании Unix-сокета в PGHOST указывается каталог сокета, а не имя файла.
Способ аутентификации в этом случае определяется конфигурацией PostgreSQL.

## Миграции и пользователи

```bash
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

migrate создаёт таблицы приложения, авторизации, сессий и административного журнала.
createsuperuser интерактивно создаёт администратора. Обычного автора конференции
следует зарегистрировать через сайт: это позволяет показать различие ролей.

Откройте http://127.0.0.1:8000/. Для другого порта:

```bash
python manage.py runserver 127.0.0.1:8002
```

Изменение порта приложения не меняет порт PostgreSQL.

## Учебные данные

seed_demo добавляет восемь конференций с тематикой «Информатика», двух владельцев,
четыре автомобиля, удостоверения и шесть записей владения. Все личные сведения
учебные. Пароли демонстрационных владельцев отключены.

Команда проверяет наличие своих записей и допускает повторный запуск.
Она не создаёт администратора и не задаёт пароль для входа.
Зарегистрированные выступления и отзывы создаются через интерфейсы приложения.

## Запуск в PyCharm

1. Открыть каталог laboratory_work_2 или весь репозиторий курса.
2. Выбрать интерпретатор .venv/bin/python из созданного окружения Python 3.10.
3. Задать рабочий каталог laboratory_work_2 и переменные PostgreSQL.
4. Запустить manage.py с параметрами runserver 127.0.0.1:8000 либо выполнить команду в терминале.
5. Для тестов использовать тот же интерпретатор и те же параметры БД.

Django-интеграция PyCharm Professional удобна, но не обязательна: управление
проектом доступно через обычный терминал.

## Типовые проблемы

| Сообщение или симптом | Что проверить |
|---|---|
| Connection refused | PostgreSQL запущен, PGHOST и PGPORT совпадают с его настройками |
| Password authentication failed | PGUSER, пароль и правила доступа PostgreSQL |
| Database does not exist | Создана ли база из PGDATABASE |
| Permission denied to create database при тестах | У учебной роли есть CREATEDB |
| Relation does not exist | Выполнена команда migrate |
| DisallowedHost | Открыт localhost/127.0.0.1 либо хост добавлен в DJANGO_ALLOWED_HOSTS |
| ModuleNotFoundError | Активировано нужное окружение, установлены зависимости |
| Порт занят | Остановить прежний runserver либо выбрать другой порт |
| Каталог пуст | Выполнить seed_demo или создать конференции через admin |
| Нет ссылки «Участники» | Вход выполнен обычным пользователем, а не is_staff |

Сайт предназначен для локальной учебной демонстрации. Публикуется статический
отчёт MkDocs; приложение Django на GitHub Pages не запускается.

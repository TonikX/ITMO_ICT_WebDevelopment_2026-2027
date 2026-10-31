# Примеры работы

Ниже — реальные выводы команд и HTTP-ответов, полученные при проверке проекта
(dev-сервер Django, Python 3.9, Django 3.2.25, база SQLite).

## Инициализация и демо-данные

```text
$ python manage.py migrate
  Applying homework.0001_initial... OK
  Applying sessions.0001_initial... OK

$ python manage.py seed_demo
OK: заданий=9, пользователей=4, новых работ=6

$ python manage.py seed_demo        # повторный запуск — идемпотентен
OK: заданий=9, пользователей=4, новых работ=0
```

## Тесты

```text
$ python manage.py test homework
...............

Ran 15 tests in 2.129s
OK
```

## HTTP-проверки страниц (curl)

```text
$ curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/
200

$ curl -s "http://127.0.0.1:8765/?page=2" | grep -o "Страница 2 из [0-9]*"
Страница 2 из 2

$ curl -s "http://127.0.0.1:8765/?subject=Алгебра" | grep -o "Алгебра" | wc -l   # фильтр
4   # только задания по алгебре

# Список предметов в выпадающем списке фильтра — distinct()
$ curl -s http://127.0.0.1:8765/ | grep -o '<option value="[^"]*"' | sort -u
<option value=""
<option value="Алгебра"
<option value="Английский"
<option value="Геометрия"
<option value="Информатика"
<option value="История"
<option value="Физика"
<option value="Химия"
```

## Логин ученика и страница задания (cookie-сессия)

```text
$ curl -c ck.txt http://127.0.0.1:8765/accounts/login/ > login.html
$ TOKEN=$(grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' login.html | cut -d'"' -f4)
$ curl -b ck.txt -c ck.txt -o /dev/null -w "%{http_code} -> %{redirect_url}\n" \
      -d "csrfmiddlewaretoken=$TOKEN" -d username=ivan -d password=student123 \
      -d next=/ -e http://127.0.0.1:8765/accounts/login/ http://127.0.0.1:8765/accounts/login/
302 -> http://127.0.0.1:8765/
```

После входа на странице оценённого задания ученик видит отметку и дату:

```text
$ curl -s -b ck.txt http://127.0.0.1:8765/homework/9/ | grep -o "Оценка: <strong>[0-9]*</strong>"
Оценка: <strong>5</strong>
```

Страница неоценённой работы содержит форму сдачи:

```text
$ curl -s -b ck.txt http://127.0.0.1:8765/homework/3/ | grep -o "Отправить на проверку"
Отправить на проверку
```

## Режим учителя

```text
# Админка содержит наши модели
$ curl -s -b ck_t.txt http://127.0.0.1:8765/admin/ | grep -o "Сданные работы"
Сданные работы

# Учитель видит все сданные работы по заданию и ссылку на админку
$ curl -s -b ck_t.txt http://127.0.0.1:8765/homework/9/ | grep -o "Сданные работы: [0-9]*"
Сданные работы: 2

# Сводка: режим учителя + выбор группы + таблица по всем классам
$ curl -s -b ck_t.txt http://127.0.0.1:8765/summary/ | grep -oE "режим учителя|Сводка по всем классам|K3339|K3331"
режим учителя
K3331
K3339
Сводка по всем классам
```

## Sitemap проверенных URL (статусы по ролям)

| URL | Аноним | Ученик | Учитель |
|-----|:------:|:------:|:-------:|
| `/` | 200 | 200 | 200 |
| `/homework/<pk>/` | 200 | 200 (форма/решение) | 200 (все работы) |
| `/my/` | 302 → login | 200 | 200 |
| `/summary/` | 200 (пусто) | 200 (свой класс) | 200 (любая группа) |
| `/register/` | 200 | — | — |
| `/accounts/login/` | 200 | — | — |
| `/admin/` | 302 → login | 302 → login | 200 |

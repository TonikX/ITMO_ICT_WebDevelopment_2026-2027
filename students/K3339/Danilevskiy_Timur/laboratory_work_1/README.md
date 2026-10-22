# Лабораторная работа 1. Работа с сокетами

Данилевский Тимур, K3339. Вариант задания 2 — 3 (площадь трапеции).

Нужен только Python 3.8+, сторонние библиотеки не используются.
Сервер и клиент запускаются в разных терминалах, сервер — первым.

| Задание | Запуск |
|---------|--------|
| 1. UDP: Hello, server / Hello, client | `python task1/server.py`, затем `python task1/client.py` |
| 2. TCP: площадь трапеции | `python task2/server.py`, затем `python task2/client.py` |
| 3. HTTP: отдача index.html | `python task3/server.py`, открыть http://127.0.0.1:8080/ |
| 4. Многопользовательский чат | `python task4/server.py`, затем `python task4/client.py` в нескольких терминалах |
| 5. Веб-сервер оценок (GET/POST) | `python task5/server.py`, открыть http://127.0.0.1:8081/ |

Команды чата: `/users` — список участников, `/exit` — выход.

Отчёт оформлен в MkDocs: `docs/lr1/report.md` в корне репозитория.

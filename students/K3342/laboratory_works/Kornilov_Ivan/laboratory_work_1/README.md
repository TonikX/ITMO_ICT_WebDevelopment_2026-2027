# Лабораторная работа 1

Код лежит в `students/K3342/laboratory_works/Kornilov_Ivan/laboratory_work_1`.
Все серверы слушают `localhost:8080`. Сначала запускается сервер, потом клиент.

## Задание 1. UDP

```bash
python3 task_1/server.py
python3 task_1/client.py
```

## Задание 2. TCP, теорема Пифагора

```bash
python3 task_2/server.py
python3 task_2/client.py
```

Пример ввода: `3 4`. Ожидаемый ответ: гипотенуза `5`.

## Задание 3. HTML по HTTP

```bash
python3 task_3/server.py
```

Открыть в браузере: http://localhost:8080/

## Задание 4. Многопользовательский чат

```bash
python3 task_4/server.py
python3 task_4/client.py
```

Клиент один. Нужно запустить его в нескольких терминалах. Выход: `/exit`.

## Задание 5. Журнал оценок

```bash
python3 task_5/server.py
```

Открыть в браузере: http://localhost:8080/

## Просмотр отчёта на сайте

Из корня репозитория:

```bash
python3 -m pip install mkdocs mkdocs-material
python3 -m mkdocs serve
```

Отчёт по ЛР1: http://127.0.0.1:8000/report1/
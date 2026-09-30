# ЛР1. Работа с сокетами

В папке находятся все пять заданий.
Отчёт и конфигурация MkDocs находятся в корне репозитория курса:
`docs/lr1/report.md` и `mkdocs.yml`.

## Запуск в любом репозитории

Нужен Python 3.10+. Команды программ выполняются **из родительской папки**
относительно этого README. Из корня репозитория курса перейдите в папку автора:

```sh
cd students/K3341/laboratory_works/Gritsenko_Yaroslav
```

Если терминал открыт в этой папке лабораторной, сначала выполните `cd ..`.

| Задание | Сервер, отдельный терминал | Клиент / браузер |
|---|---|---|
| UDP | `python3 -m laboratory_work_1.task1.server` | `python3 -m laboratory_work_1.task1.client` |
| Площадь трапеции | `python3 -m laboratory_work_1.task2.server` | `python3 -m laboratory_work_1.task2.client` |
| HTML | `python3 -m laboratory_work_1.task3.server` | `http://127.0.0.1:9003/` |
| Чат | `python3 -m laboratory_work_1.task4.server` | `python3 -m laboratory_work_1.task4.client --name Алиса` |
| Оценки | `python3 -m laboratory_work_1.task5.server` | `http://127.0.0.1:9005/` |

Задание 2: вариант 3 — площадь трапеции, номер в журнале 11.
Для чата запустите три экземпляра клиента с разными именами; выход — `/quit`.
Все серверы завершаются Ctrl+C, адрес по умолчанию — `127.0.0.1`.
Сторонние зависимости для программ не нужны.

Оценки хранятся только в памяти: после остановки сервера журнал пустой.

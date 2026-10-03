# Лабораторная работа №2 — Отели

Django-проект для просмотра номеров, бронирования и добавления отзывов.
Отчёт находится в папке `docs/`, его настройки — в `mkdocs.yml`.

## Отчёт MkDocs

Выполните команды из папки `laboratory_work_2`:

```bash
source venv/bin/activate
pip install mkdocs
mkdocs serve -a 127.0.0.1:8001
```

Отчёт доступен по адресу http://127.0.0.1:8001/.
Порт 8001 позволяет одновременно запускать Django на порту 8000.
Для остановки нажмите `Ctrl+C`.

Проверка сборки отчёта:

```bash
mkdocs build --strict --site-dir /tmp/hotel-lab2-report
```

Для добавления скриншотов используйте инструкции в `docs/images/README.txt`.

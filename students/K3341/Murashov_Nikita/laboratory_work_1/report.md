# ЛР1. Отчёт — Сокеты

## Вариант

Порядковый номер 17. Задание 2: `((17-1) % 4) + 1 = 1` — теорема Пифагора.

## Запуск

```bash
python task1/server.py
python task1/client.py

python task2/server.py
python task2/client.py   # ввод: Катет a, Катет b

python task3/server.py
curl -i http://127.0.0.1:11003/

python task4/server.py
python task4/client.py   # в разных терминалах, выход: /exit

python task5/server.py
curl http://127.0.0.1:11005/
curl -X POST -d "subject=Математика&grade=5" http://127.0.0.1:11005/
```

## Протоколы

- Задание 1: UDP `sendto`/`recvfrom`, без соединения.
- Задание 2: TCP, строка `a b` → гипотенуза или `error: ...`.
- Задание 3: TCP + HTTP вручную, `Content-Length` от байт тела.
- Задание 4: TCP + `threading`, `dict[имя, сокет]`, рассылка всем кроме автора, `/exit`.
- Задание 5: TCP + HTTP вручную, `dict[предмет, оценки]` группирует через `setdefault`.

## Примеры работы

- Задание 1: клиент получил `Hello, client`.
- Задание 2: `3 4` → `5.0000`.
- Задание 3: страница открылась, `Content-Length` совпал.
- Задание 4: `alice: hello bob` дошло до `bob`; `* bob вышел` дошло до `alice`.
- Задание 5: `Математика: 5, 4` в одной строке таблицы.

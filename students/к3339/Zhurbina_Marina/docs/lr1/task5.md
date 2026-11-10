# Задание 5. Веб-сервер (журнал оценок)

## Протокол

Веб-сервер поверх **TCP** обрабатывает HTTP-запросы GET и POST. Запрос разбирается
вручную: определяется метод и путь, для POST читается тело по `Content-Length`.
Оценки хранятся в словаре «предмет → список оценок» и отдаются HTML-страницей.

| Параметр  | Значение                        |
|-----------|---------------------------------|
| Протокол  | HTTP поверх TCP (`SOCK_STREAM`) |
| Адрес     | `127.0.0.1`                     |
| Порт      | `9005`                          |
| Обработка | последовательная (без потоков)  |

## Эндпоинты

| Метод  | URL       | Описание                                                      |
|--------|-----------|---------------------------------------------------------------|
| `POST` | `/grade`  | Сохранить оценку. Тело: `предмет=Алгебра&оценка=5`            |
| `GET`  | `/`       | HTML-страница со списком оценок, сгруппированных по предметам |
| `GET`  | `/grades` | То же, что `/`                                                |

## Модель данных

Журнал — словарь `journal` вида «предмет → список оценок». Группировка по предмету:
две оценки по «Алгебре» хранятся как одна запись `Алгебра: [5, 4]`, а не как две
отдельные строки.

## Код сервера

```python
import socket
from html import escape
from urllib.parse import unquote

ADDRESS = "127.0.0.1"
PORT = 9005

journal = {}


def read_form(body):
    fields = body.split("&")
    parsed = {}
    for part in fields:
        if "=" in part:
            key, value = part.split("=", 1)
            parsed[unquote(key)] = unquote(value)
    return parsed


def save_mark(body):
    data = read_form(body)
    subject = data.get("предмет", "")
    score = data.get("оценка", "")
    if not subject or not score:
        return "400 Bad Request", "Не указан предмет или оценка"

    if subject in journal:
        journal[subject].append(score)
    else:
        journal[subject] = [score]

    return "200 OK", f"Сохранено: {subject} = {score}"


def make_page():
    lines = []
    if not journal:
        lines.append("<p>Журнал пуст.</p>")
    else:
        lines.append("<ul>")
        for subject, scores in journal.items():
            safe = ", ".join(escape(s) for s in scores)
            lines.append(f"<li>{escape(subject)}: {safe}</li>")
        lines.append("</ul>")

    page = "<h1>Журнал оценок</h1>" + "".join(lines)
    return page


def respond(conn, request):
    lines = request.split("\r\n")
    head = lines[0].split()
    if len(head) < 2:
        conn.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
        return

    method, path = head[0], head[1]
    body = ""
    if method == "POST":
        length = 0
        for line in lines[1:]:
            if line.lower().startswith("content-length:"):
                length = int(line.split(":", 1)[1].strip())
        if length:
            body = request.split("\r\n\r\n", 1)[1][:length]

    if method == "GET" and path in ("/", "/grades"):
        status = "200 OK"
        payload = make_page().encode("utf-8")
    elif method == "POST" and path == "/grade":
        status, text = save_mark(body)
        payload = text.encode("utf-8")
    else:
        status = "404 Not Found"
        payload = "Страница не найдена".encode("utf-8")

    header = (f"HTTP/1.1 {status}\r\nContent-Type: text/html; charset=utf-8\r\n"
              f"Content-Length: {len(payload)}\r\nConnection: close\r\n\r\n")
    conn.sendall(header.encode("utf-8") + payload)


def process(conn, address):
    request = conn.recv(65536).decode("utf-8", errors="replace")
    if request:
        print(f"{address}: {request.splitlines()[0]}")
        respond(conn, request)
    conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ADDRESS, PORT))
    server.listen(5)
    print(f"Сервер на http://{ADDRESS}:{PORT}")

    while True:
        conn, address = server.accept()
        process(conn, address)


main()
```

## Пример работы в терминале

** Окно
1 — сервер: **

```
> python src/task5/server.py
> Сервер на http://127.0.0.1:9005
('127.0.0.1', 55001): POST /grade HTTP/1.1
('127.0.0.1', 55002): GET / HTTP/1.1
```

**Добавление оценок (curl):**

```
> curl -X POST --data "предмет=Алгебра&оценка=5" http://127.0.0.1:9005/grade
> Сохранено: Алгебра = 5
> curl -X POST --data "предмет=Алгебра&оценка=4" http://127.0.0.1:9005/grade
> Сохранено: Алгебра = 4
> curl -X POST --data "предмет=Геометрия&оценка=5" http://127.0.0.1:9005/grade
> Сохранено: Геометрия = 5
```

**GET `/`:** страница показывает `Алгебра: 5, 4` и `Геометрия: 5` — по одной записи на предмет.

## Запуск

1. Терминал 1: `python src/task5/server.py`
2. Добавить оценки через `curl` и открыть `http://127.0.0.1:9005/`.
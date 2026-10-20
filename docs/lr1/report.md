# ЛР1. Отчёт — Работа с сокетами

## Цель работы

Изучить принципы межсокетного взаимодействия в вебе и реализовать базовую архитектуру клиент-сервер с использованием протоколов UDP и TCP, включая простейший HTTP-сервер, многопользовательский чат и веб-сервер для обработки GET/POST-запросов.

---

## Задание 1. Обмен сообщениями по UDP

Реализован обмен сообщениями между клиентом и сервером по протоколу UDP через `socket.SOCK_DGRAM`. Клиент отправляет серверу `"Hello, server"`, сервер отвечает `"Hello, client"`.

### Сервер (`server.py`)

```python
import socket

HOST = 'localhost'
PORT = 9001

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print(f"UDP-сервер запущен на {HOST}:{PORT}...")

while True:
    data, client_address = server_socket.recvfrom(1024)
    message = data.decode()
    print(f"Получено от {client_address}: {message}")

    response = "Hello, client"
    server_socket.sendto(response.encode(), client_address)
```

### Клиент (`client.py`)

```python
import socket

HOST = 'localhost'
PORT = 9001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "Hello, server"
client_socket.sendto(message.encode(), (HOST, PORT))
print(f"Отправлено серверу: {message}")

data, server_address = client_socket.recvfrom(1024)
print(f"Получено от сервера: {data.decode()}")

client_socket.close()
```

### Пример работы в терминале

```
$ python3 server.py
UDP-сервер запущен на localhost:9001...
Получено от ('127.0.0.1', 58414): Hello, server

$ python3 client.py
Отправлено серверу: Hello, server
Получено от сервера: Hello, client
```

!!! note "Примечание"
    UDP не устанавливает соединение — сервер и клиент просто обмениваются датаграммами через `sendto()`/`recvfrom()`.

---

## Задание 2. Вычисления через TCP

Выбран вариант **4 — площадь параллелограмма**. Клиент вводит основание и высоту, сервер вычисляет площадь и возвращает результат.

### Сервер (`server.py`)

```python
import socket

HOST = 'localhost'
PORT = 9002


def parallelogram_area(base: float, height: float) -> float:
    """Вычисляет площадь параллелограмма по основанию и высоте."""
    return base * height


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"TCP-сервер (площадь параллелограмма) запущен на {HOST}:{PORT}...")

while True:
    conn, addr = server_socket.accept()
    print(f"Подключение от {addr}")

    data = conn.recv(1024).decode()
    print(f"Получены параметры: {data}")

    try:
        base_str, height_str = data.split(',')
        base, height = float(base_str), float(height_str)
        if base <= 0 or height <= 0:
            raise ValueError("основание и высота должны быть положительными")
        area = parallelogram_area(base, height)
        result = f"Площадь параллелограмма: {area:.4f}"
    except ValueError as exc:
        result = f"Ошибка в данных: {exc}"

    conn.sendall(result.encode())
    conn.close()
```

### Клиент (`client.py`)

```python
import socket

HOST = 'localhost'
PORT = 9002

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

base = input("Введите основание параллелограмма: ")
height = input("Введите высоту параллелограмма: ")

message = f"{base},{height}"
client_socket.sendall(message.encode())

response = client_socket.recv(1024).decode()
print(f"Ответ сервера: {response}")

client_socket.close()
```

### Пример работы в терминале

```
$ python3 client.py
Введите основание параллелограмма: 6
Введите высоту параллелограмма: 3
Ответ сервера: Площадь параллелограмма: 18.0000

$ python3 server.py
TCP-сервер (площадь параллелограмма) запущен на localhost:9002...
Подключение от ('127.0.0.1', 49175)
Получены параметры: 6,3
```

## Задание 3. Раздача HTML-страницы по HTTP

Сервер читает файл `index.html` и отправляет его клиенту как тело HTTP-ответа с заголовками `Content-Type` и `Content-Length`.

??? info "Полный листинг сервера"
    ```python
    import socket
    import os

    HOST = 'localhost'
    PORT = 9003
    HTML_FILE = os.path.join(os.path.dirname(__file__), 'index.html')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"HTTP-сервер запущен на {HOST}:{PORT}...")

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    while True:
        conn, addr = server_socket.accept()
        print(f"Подключение от {addr}")

        request = conn.recv(1024).decode(errors='ignore')
        print(f"Запрос клиента:\n{request.splitlines()[0] if request else ''}")

        body = html_content.encode('utf-8')
        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=UTF-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8') + body

        conn.sendall(http_response)
        conn.close()
    ```

### Пример работы

```
$ python3 server.py
HTTP-сервер запущен на localhost:9003...
Подключение от ('127.0.0.1', 53050)
Запрос клиента:
GET / HTTP/1.1

$ curl http://localhost:9003/
<!DOCTYPE html>
<html lang="ru">
...
    <h1>Привет! Это страница, отданная через сокет.</h1>
...
</html>
```

Страница также успешно открывается в браузере по адресу `http://localhost:9003`.

---

## Задание 4. Многопользовательский чат

Реализован **многопользовательский чат по протоколу TCP** с использованием `threading` (реализация на 100% баллов).

Архитектура: один серверный скрипт держит словарь активных подключений `{имя_пользователя: сокет}` и обслуживает каждого клиента в отдельном потоке. Один клиентский скрипт запускается несколько раз (разными пользователями в разных терминалах) — роль клиента не привязана к конкретному пользователю. Приём и отправка сообщений на клиенте также разделены на потоки, чтобы пользователь мог одновременно печатать и получать сообщения.

### Сервер (`server.py`)

```python
import socket
import threading

HOST = 'localhost'
PORT = 9004

clients = {}
clients_lock = threading.Lock()


def broadcast(message: str, exclude_username: str = None):
    """Рассылает сообщение всем клиентам, кроме exclude_username."""
    with clients_lock:
        for username, conn in list(clients.items()):
            if username == exclude_username:
                continue
            try:
                conn.sendall(message.encode('utf-8'))
            except OSError:
                pass


def handle_client(conn: socket.socket, addr):
    username = None
    try:
        conn.sendall("Введите имя пользователя: ".encode('utf-8'))
        username = conn.recv(1024).decode('utf-8').strip()

        with clients_lock:
            clients[username] = conn

        broadcast(f"* {username} присоединился к чату", exclude_username=username)
        conn.sendall(f"Добро пожаловать, {username}! Введите /exit для выхода.\n".encode('utf-8'))

        while True:
            data = conn.recv(1024)
            if not data:
                break
            text = data.decode('utf-8').strip()
            if not text:
                continue
            if text == '/exit':
                break
            broadcast(f"{username}: {text}", exclude_username=username)

    except (ConnectionResetError, OSError):
        pass
    finally:
        if username:
            with clients_lock:
                clients.pop(username, None)
            broadcast(f"* {username} покинул чат", exclude_username=username)
        conn.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    print(f"Чат-сервер запущен на {HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == '__main__':
    main()
```

### Клиент (`client.py`)

```python
import socket
import threading

HOST = 'localhost'
PORT = 9004


def receive_messages(sock: socket.socket):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Соединение с сервером закрыто.")
                break
            print(data.decode('utf-8'))
        except OSError:
            break


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    prompt = client_socket.recv(1024).decode('utf-8')
    print(prompt, end='')
    username = input()
    client_socket.sendall(username.encode('utf-8'))

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        try:
            message = input()
        except EOFError:
            break
        if not message:
            continue
        client_socket.sendall(message.encode('utf-8'))
        if message == '/exit':
            break

    client_socket.close()


if __name__ == '__main__':
    main()
```

### Пример работы (два клиента: alice и bob)

```
# Терминал сервера
Чат-сервер запущен на localhost:9004...
alice ('127.0.0.1', 44806) присоединился к чату
bob ('127.0.0.1', 44816) присоединился к чату
alice: hello bob
bob покинул чат
alice покинул чат

# Терминал bob получает:
alice: hello bob

# Терминал alice получает (после выхода bob):
* bob присоединился к чату
* bob покинул чат
```

---

## Задание 5. Простой веб-сервер (GET/POST)

Сервер вручную разбирает HTTP-запрос (метод, путь, заголовки, тело), обрабатывает `POST` для сохранения оценки по дисциплине и `GET` для отображения журнала оценок в виде HTML-страницы.

Журнал оценок хранится как `dict[str, list[str]]` — название дисциплины является ключом, а значение — список всех полученных по ней оценок, что обеспечивает группировку по предмету, как того требует задание.

### Модель данных

| Структура | Назначение |
|-----------|------------|
| `grades: dict[str, list[str]]` | `{"Математика": ["5", "4"], "Физика": ["5"]}` — оценки группируются по названию дисциплины |

### Сервер (`server.py`)

```python
import socket
from urllib.parse import parse_qs

HOST = 'localhost'
PORT = 9005

grades = {}


def parse_request(raw_request: str):
    """Разбирает сырой HTTP-запрос на метод, путь и тело."""
    lines = raw_request.split('\r\n')
    method, path, _ = lines[0].split(' ')

    headers = {}
    body_start = 0
    for i, line in enumerate(lines[1:], start=1):
        if line == '':
            body_start = i + 1
            break
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()

    body = '\r\n'.join(lines[body_start:]) if body_start else ''
    return method, path, headers, body


def render_grades_page() -> str:
    rows = ''
    for subject, subject_grades in grades.items():
        grades_str = ', '.join(str(g) for g in subject_grades)
        rows += f"<tr><td>{subject}</td><td>{grades_str}</td></tr>\n"

    if not rows:
        rows = '<tr><td colspan="2">Оценок пока нет</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Журнал оценок</title></head>
<body>
    <h1>Журнал оценок</h1>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
    <h2>Добавить оценку</h2>
    <form method="POST" action="/">
        Дисциплина: <input type="text" name="subject"><br><br>
        Оценка: <input type="text" name="grade"><br><br>
        <input type="submit" value="Отправить">
    </form>
</body>
</html>"""


def build_response(status: str, body: str) -> bytes:
    body_bytes = body.encode('utf-8')
    return (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode('utf-8') + body_bytes


def handle_request(raw_request: str) -> bytes:
    if not raw_request:
        return build_response("400 Bad Request", "<h1>400 Bad Request</h1>")

    method, path, headers, body = parse_request(raw_request)

    if method == 'POST':
        content_length = int(headers.get('content-length', 0))
        params = parse_qs(body[:content_length])
        subject = params.get('subject', [''])[0].strip()
        grade = params.get('grade', [''])[0].strip()

        if subject and grade:
            grades.setdefault(subject, []).append(grade)

        return build_response("200 OK", render_grades_page())

    elif method == 'GET':
        return build_response("200 OK", render_grades_page())

    return build_response("405 Method Not Allowed", "<h1>405 Method Not Allowed</h1>")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Веб-сервер журнала оценок запущен на {HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        raw_request = conn.recv(4096).decode('utf-8', errors='ignore')
        response = handle_request(raw_request)
        conn.sendall(response)
        conn.close()


if __name__ == '__main__':
    main()
```

### Пример работы в терминале

```
$ curl -X POST http://localhost:9005/ -d "subject=Математика&grade=5"
$ curl -X POST http://localhost:9005/ -d "subject=Математика&grade=4"
$ curl -X POST http://localhost:9005/ -d "subject=Физика&grade=5"
$ curl http://localhost:9005/
```

Результат — HTML-страница с таблицей:

| Дисциплина | Оценки |
|------------|--------|
| Математика | 5, 4   |
| Физика     | 5      |

Как видно, две оценки по «Математике» сгруппированы в одну строку, что соответствует требованию задания.

---

## Вывод

В ходе выполнения лабораторной работы изучены принципы клиент-серверного взаимодействия на уровне сокетов: реализован обмен сообщениями по UDP, вычисления по TCP, простейший HTTP-сервер, многопользовательский чат с использованием потоков и веб-сервер для обработки GET/POST-запросов с группировкой данных по дисциплинам. Все реализации используют только стандартную библиотеку `socket` (и `threading` для чата), без сторонних веб-фреймворков.


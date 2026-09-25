# Лабораторная работа №1. Сокеты и клиент-серверное взаимодействие

## Цель работы

Изучить принципы сокетного взаимодействия в вебе и научиться реализовывать базовую архитектуру клиент-сервер с использованием протоколов UDP, TCP и HTTP.

---

## Практическое задание 1. Обмен сообщениями по UDP

В первом задании реализованы клиентская и серверная части приложения с использованием протокола UDP.

Клиент отправляет серверу сообщение:

```text
Hello, server
```

Сервер получает сообщение, выводит его в консоль и отправляет клиенту ответ:

```text
Hello, client
```

Для работы с UDP используется:

```python
socket.SOCK_DGRAM
```

### Сервер

Сервер создаёт UDP-сокет, привязывает его к адресу `127.0.0.1` и порту `5000`, после чего ожидает сообщение от клиента с помощью `recvfrom()`.

После получения сообщения сервер отправляет ответ клиенту с помощью `sendto()`.

```python
import socket


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))

        print(f"UDP-сервер запущен на {HOST}:{PORT}")
        print("Ожидание сообщения от клиента...")

        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        message = data.decode("utf-8")

        print(f"Получено от клиента: {message}")

        response = "Hello, client"
        server_socket.sendto(response.encode("utf-8"), client_address)

        print(f"Ответ отправлен клиенту: {response}")


if __name__ == "__main__":
    main()
```

### Клиент

Клиент создаёт UDP-сокет, отправляет сообщение `Hello, server`, затем ожидает ответ сервера и выводит его в консоль.

```python
import socket


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        message = "Hello, server"

        client_socket.sendto(
            message.encode("utf-8"),
            (SERVER_HOST, SERVER_PORT),
        )

        print(f"Отправлено серверу: {message}")

        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        response = data.decode("utf-8")

        print(f"Получено от сервера: {response}")


if __name__ == "__main__":
    main()
```

### Результат работы

Сервер:

```text
UDP-сервер запущен на 127.0.0.1:5000
Ожидание сообщения от клиента...
Получено от клиента: Hello, server
Ответ отправлен клиенту: Hello, client
```

Клиент:

```text
Отправлено серверу: Hello, server
Получено от сервера: Hello, client
```

---

## Практическое задание 2. Вычисления через TCP

Во втором задании реализовано клиент-серверное приложение с использованием протокола TCP.

Используется вариант 4 — вычисление площади параллелограмма.

Площадь вычисляется по формуле:

```text
S = a * h
```

где `a` — основание параллелограмма, `h` — его высота.

Для работы с TCP используется:

```python
socket.SOCK_STREAM
```

### Сервер

Сервер принимает подключение клиента, получает основание и высоту, вычисляет площадь и отправляет результат обратно клиенту.

```python
import socket


HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print(f"TCP-сервер запущен на {HOST}:{PORT}")
        print("Ожидание подключения клиента...")

        connection, client_address = server_socket.accept()

        with connection:
            print(f"Клиент подключён: {client_address}")

            data = connection.recv(BUFFER_SIZE).decode("utf-8")
            base, height = map(float, data.split())

            print(f"Получено основание: {base}")
            print(f"Получена высота: {height}")

            area = base * height

            connection.sendall(str(area).encode("utf-8"))

            print(f"Площадь параллелограмма: {area}")
            print("Результат отправлен клиенту.")


if __name__ == "__main__":
    main()
```

### Клиент

Клиент запрашивает у пользователя основание и высоту, подключается к серверу и отправляет введённые значения.

После этого клиент получает рассчитанную сервером площадь.

```python
import socket


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 1024


def main() -> None:
    base = float(input("Введите длину основания параллелограмма: "))
    height = float(input("Введите высоту параллелограмма: "))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        print("Подключение к серверу установлено.")

        message = f"{base} {height}"
        client_socket.sendall(message.encode("utf-8"))

        data = client_socket.recv(BUFFER_SIZE)
        area = data.decode("utf-8")

        print(f"Площадь параллелограмма: {area}")


if __name__ == "__main__":
    main()
```

### Результат работы

Клиент:

```text
Введите длину основания параллелограмма: 8
Введите высоту параллелограмма: 5
Подключение к серверу установлено.
Площадь параллелограмма: 40.0
```

Сервер:

```text
TCP-сервер запущен на 127.0.0.1:5001
Ожидание подключения клиента...
Клиент подключён: ('127.0.0.1', ...)
Получено основание: 8.0
Получена высота: 5.0
Площадь параллелограмма: 40.0
Результат отправлен клиенту.
```

---

## Практическое задание 3. Раздача HTML-страницы по HTTP

В третьем задании реализован HTTP-сервер с использованием библиотеки `socket`.

Сервер принимает запрос от браузера, загружает содержимое файла `index.html`, формирует HTTP-ответ и отправляет HTML-страницу клиенту.

### Сервер

```python
import socket


HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"HTTP-сервер запущен на {HOST}:{PORT}")
        print("Откройте в браузере: http://127.0.0.1:8080")
        print("Ожидание HTTP-запросов...")

        while True:
            client_socket, client_address = server_socket.accept()

            with client_socket:
                request = client_socket.recv(BUFFER_SIZE).decode(
                    "utf-8",
                    errors="ignore",
                )

                if not request:
                    continue

                request_line = request.splitlines()[0]

                print(f"Подключён клиент: {client_address}")
                print(f"Получен запрос: {request_line}")

                with open("index.html", "rb") as html_file:
                    body = html_file.read()

                headers = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8")

                client_socket.sendall(headers + body)

                print("HTML-страница отправлена клиенту.")


if __name__ == "__main__":
    main()
```

### HTML-страница

Файл `index.html` содержит содержимое страницы, которое сервер отправляет браузеру.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Задание 3</title>
</head>
<body>
    <h1>Веб-сервер работает успешно</h1>

    <div>
        HTML-страница получена с сервера, реализованного с помощью библиотеки socket
    </div>
</body>
</html>
```

### Результат работы

Сервер:

```text
HTTP-сервер запущен на 127.0.0.1:8080
Откройте в браузере: http://127.0.0.1:8080
Ожидание HTTP-запросов...

Подключён клиент: ('127.0.0.1', ...)
Получен запрос: GET / HTTP/1.1
HTML-страница отправлена клиенту.
```

В браузере отображается:

```text
Веб-сервер работает успешно

HTML-страница получена с сервера, реализованного с помощью библиотеки socket
```

---

## Практическое задание 4. Многопользовательский чат

В четвёртом задании реализован многопользовательский чат с использованием TCP и библиотеки `threading`.

Каждый пользователь запускает один и тот же файл `client.py`.

После подключения пользователь вводит своё имя. Сервер хранит активные подключения и передаёт сообщения между пользователями.

### Сервер

```python
import socket
import threading


HOST = "127.0.0.1"
PORT = 5002
ENCODING = "utf-8"


class ChatServer:
    def __init__(self) -> None:
        self._clients: dict[socket.socket, str] = {}
        self._clients_lock = threading.Lock()

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()

            print(f"TCP-чат запущен на {HOST}:{PORT}")
            print("Ожидание подключений...")

            while True:
                client_socket, client_address = server_socket.accept()

                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address),
                    daemon=True,
                )
                thread.start()

    def _handle_client(
        self,
        client_socket: socket.socket,
        client_address: tuple[str, int],
    ) -> None:
        username = None

        try:
            reader = client_socket.makefile(
                "r",
                encoding=ENCODING,
                newline="\n",
            )

            username = reader.readline().strip()

            with self._clients_lock:
                self._clients[client_socket] = username

            self._send(
                client_socket,
                f"OK Добро пожаловать в чат, {username}!",
            )

            print(f"Подключён пользователь {username}: {client_address}")

            self._broadcast(
                f"[Система] Пользователь {username} вошёл в чат.",
                exclude=client_socket,
            )

            for line in reader:
                message = line.rstrip("\n")

                if message == "/exit":
                    break

                if not message:
                    continue

                print(f"{username}: {message}")

                self._broadcast(
                    f"{username}: {message}",
                    exclude=client_socket,
                )
        finally:
            with self._clients_lock:
                if client_socket in self._clients:
                    del self._clients[client_socket]

            client_socket.close()

            if username is not None:
                print(f"Пользователь {username} отключился.")
                self._broadcast(
                    f"[Система] Пользователь {username} вышел из чата."
                )

    def _broadcast(
        self,
        message: str,
        exclude: socket.socket | None = None,
    ) -> None:
        with self._clients_lock:
            recipients = [
                client_socket
                for client_socket in self._clients
                if client_socket is not exclude
            ]

        for client_socket in recipients:
            try:
                self._send(client_socket, message)
            except OSError:
                pass

    @staticmethod
    def _send(client_socket: socket.socket, message: str) -> None:
        client_socket.sendall(f"{message}\n".encode(ENCODING))


if __name__ == "__main__":
    ChatServer().run()
```

### Клиент

Клиент подключается к серверу, передаёт имя пользователя и запускает отдельный поток для получения входящих сообщений.

```python
import socket
import threading


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002
ENCODING = "utf-8"


class ChatClient:
    def __init__(self) -> None:
        self._socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self._reader = None

    def run(self) -> None:
        username = input("Введите имя пользователя: ").strip()

        self._socket.connect((SERVER_HOST, SERVER_PORT))
        self._reader = self._socket.makefile(
            "r",
            encoding=ENCODING,
            newline="\n",
        )

        self._send(username)

        response = self._reader.readline().rstrip("\n")

        print(response.removeprefix("OK "))
        print("Введите сообщение.")
        print("Для выхода из чата введите /exit")

        receiver = threading.Thread(
            target=self._receive_messages,
            daemon=True,
        )
        receiver.start()

        while True:
            message = input()

            if not message:
                continue

            self._send(message)

            if message == "/exit":
                break

        self._socket.close()

    def _receive_messages(self) -> None:
        if self._reader is None:
            return

        try:
            for line in self._reader:
                message = line.rstrip("\n")

                if message:
                    print(message)
        except OSError:
            pass

    def _send(self, message: str) -> None:
        self._socket.sendall(f"{message}\n".encode(ENCODING))


if __name__ == "__main__":
    ChatClient().run()
```

### Результат работы

Пользователь Мария:

```text
Введите имя пользователя: Мария
Добро пожаловать в чат, Мария!
Введите сообщение.
Для выхода из чата введите /exit
[Система] Пользователь Дима вошёл в чат.
```

Пользователь Дима:

```text
Введите имя пользователя: Дима
Добро пожаловать в чат, Дима!
Введите сообщение.
Для выхода из чата введите /exit
```

После выхода Димы:

```text
/exit
```

у Марии выводится:

```text
[Система] Пользователь Дима вышел из чата.
```

---

## Практическое задание 5. Простой веб-сервер GET/POST

В пятом задании реализован простой веб-сервер, который вручную обрабатывает HTTP-запросы `GET` и `POST`.

Сервер позволяет вводить название дисциплины и оценку, сохранять полученные данные и отображать все оценки в виде HTML-страницы.

Оценки группируются по дисциплине.

Например:

```python
{
    "Математика": ["4", "5"],
    "Русский": ["5"],
    "Физика": ["5"],
}
```

### Сервер

```python
import html
import socket
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8081
BUFFER_SIZE = 4096
ENCODING = "utf-8"


class GradeServer:
    def __init__(self) -> None:
        self._grades: dict[str, list[str]] = {}

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )

            server_socket.bind((HOST, PORT))
            server_socket.listen()

            print(f"Веб-сервер запущен на {HOST}:{PORT}")
            print(f"Откройте в браузере: http://{HOST}:{PORT}")
            print("Ожидание HTTP-запросов...")

            while True:
                client_socket, client_address = server_socket.accept()

                with client_socket:
                    request = self._receive_request(client_socket)

                    if not request:
                        continue

                    print(f"Подключён клиент: {client_address}")
                    self._handle_request(client_socket, request)

    def _receive_request(self, client_socket: socket.socket) -> bytes:
        request = b""

        while b"\r\n\r\n" not in request:
            chunk = client_socket.recv(BUFFER_SIZE)

            if not chunk:
                return b""

            request += chunk

        headers, body = request.split(b"\r\n\r\n", 1)

        content_length = 0

        for line in headers.decode(ENCODING, errors="ignore").split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":", 1)[1].strip())

        while len(body) < content_length:
            body += client_socket.recv(BUFFER_SIZE)

        return headers + b"\r\n\r\n" + body

    def _handle_request(
        self,
        client_socket: socket.socket,
        request: bytes,
    ) -> None:
        headers, body = request.split(b"\r\n\r\n", 1)

        header_text = headers.decode(ENCODING, errors="ignore")
        request_line = header_text.split("\r\n")[0]

        method, path, _ = request_line.split(" ", 2)

        print(f"Получен запрос: {method} {path}")

        if path != "/":
            self._send_response(
                client_socket,
                "404 Not Found",
                self._build_error_page("Страница не найдена"),
            )
            return

        if method == "GET":
            self._send_response(
                client_socket,
                "200 OK",
                self._build_page(),
            )
            return

        if method == "POST":
            self._handle_post(client_socket, body)
            return

    def _handle_post(
        self,
        client_socket: socket.socket,
        body: bytes,
    ) -> None:
        form_data = parse_qs(body.decode(ENCODING))

        subject = form_data.get("subject", [""])[0].strip()
        grade = form_data.get("grade", [""])[0].strip()

        if subject not in self._grades:
            self._grades[subject] = []

        self._grades[subject].append(grade)

        print(f"Добавлена оценка: {subject} — {grade}")

        self._send_redirect(client_socket)

    def _build_page(self) -> str:
        rows = ""

        if self._grades:
            for subject, grades in self._grades.items():
                rows += (
                    "<tr>"
                    f"<td>{html.escape(subject)}</td>"
                    f"<td>{', '.join(html.escape(grade) for grade in grades)}</td>"
                    "</tr>"
                )
        else:
            rows = '<tr><td colspan="2">Оценок пока нет</td></tr>'

        return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>

    <h2>Добавить оценку</h2>

    <form method="POST" action="/">
        <label>
            Дисциплина:
            <input type="text" name="subject" required>
        </label>

        <br><br>

        <label>
            Оценка:
            <input type="text" name="grade" required>
        </label>

        <br><br>

        <button type="submit">Добавить</button>
    </form>

    <h2>Все оценки</h2>

    <table border="1" cellpadding="8">
        <tr>
            <th>Дисциплина</th>
            <th>Оценки</th>
        </tr>
        {rows}
    </table>
</body>
</html>
'''

    def _build_error_page(self, message: str) -> str:
        return f"<h1>Ошибка</h1><p>{html.escape(message)}</p>"

    def _send_response(
        self,
        client_socket: socket.socket,
        status: str,
        page: str,
    ) -> None:
        body = page.encode(ENCODING)

        headers = (
            f"HTTP/1.1 {status}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode(ENCODING)

        client_socket.sendall(headers + body)

    def _send_redirect(self, client_socket: socket.socket) -> None:
        response = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        client_socket.sendall(response.encode(ENCODING))


if __name__ == "__main__":
    GradeServer().run()
```

### Результат работы

После открытия страницы:

```text
Веб-сервер запущен на 127.0.0.1:8081
Откройте в браузере: http://127.0.0.1:8081
Ожидание HTTP-запросов...

Получен запрос: GET /
```

После добавления оценок:

```text
Получен запрос: POST /
Добавлена оценка: Математика — 4
Получен запрос: GET /

Получен запрос: POST /
Добавлена оценка: Русский — 5
Получен запрос: GET /

Получен запрос: POST /
Добавлена оценка: Физика — 5
Получен запрос: GET /
```

На HTML-странице отображается:

```text
Журнал оценок

Добавить оценку

Дисциплина: [                ]
Оценка:     [                ]

[Добавить]

Все оценки

Дисциплина      Оценки
Математика      4
Русский         5
Физика          5
```

При добавлении второй оценки для одной дисциплины она добавляется в ту же запись:

```text
Математика      4, 5
Русский         5
Физика          5
```

---

## Вывод

В ходе лабораторной работы были изучены основные способы клиент-серверного взаимодействия с использованием сокетов.

Были реализованы обмен сообщениями по UDP, вычисления через TCP, HTTP-сервер для раздачи HTML-страницы, многопользовательский TCP-чат с потоками и простой веб-сервер с обработкой GET- и POST-запросов.

В процессе выполнения работы были использованы методы `bind()`, `listen()`, `accept()`, `connect()`, `sendto()`, `recvfrom()`, `sendall()` и `recv()`, а также библиотеки `socket` и `threading`.

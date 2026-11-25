# Лабораторная работа №1. Работа с сокетами

**Студент:** Павлов Виталий, группа K3339

**Цель работы:** овладеть практическими навыками реализации клиент-серверных приложений на сокетах.

**Средства:** Python 3.11, библиотеки `socket` и `threading`.

## Задание 1. UDP

Клиент отправляет серверу сообщение «Hello, server», сервер выводит его и отвечает «Hello, client».
Обязательно использовать `socket` и протокол UDP.

Сокеты создаются с типом `SOCK_DGRAM`. В UDP нет соединения, поэтому сервер только привязывается к порту
через `bind` и ждёт датаграммы в `recvfrom`, который возвращает данные и адрес отправителя. Ответ уходит
на этот адрес через `sendto`. У клиента стоит таймаут, чтобы он не ждал вечно, если сервер не запущен.

`server.py`

```python
import socket

HOST = "127.0.0.1"
PORT = 8081

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))
print(f"UDP-сервер запущен на {HOST}:{PORT}")

while True:
    data, address = server.recvfrom(1024)
    print(f"Сообщение от {address}: {data.decode()}")
    server.sendto("Hello, client".encode(), address)
```

`client.py`

```python
import socket

SERVER = ("127.0.0.1", 8081)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(3)
client.sendto("Hello, server".encode(), SERVER)

try:
    data, address = client.recvfrom(1024)
    print(f"Ответ сервера: {data.decode()}")
except OSError:
    print("Сервер не ответил")

client.close()
```

Сервер:

```text
UDP-сервер запущен на 127.0.0.1:8081
Сообщение от ('127.0.0.1', 53398): Hello, server
```

Клиент:

```text
Ответ сервера: Hello, client
```

## Задание 2. TCP

Клиент запрашивает выполнение математической операции, параметры вводятся с клавиатуры. Сервер считает
результат и возвращает его клиенту. Вариант 2 — решение квадратного уравнения. Протокол TCP.

Сокеты имеют тип `SOCK_STREAM`. Сервер вызывает `listen` и `accept`, который возвращает отдельный сокет
для подключившегося клиента. Клиент отправляет коэффициенты одной строкой через пробел, сервер считает
дискриминант и отправляет ответ строкой. Соединение не закрывается, пока клиент не откажется продолжать:
пустой результат `recv` означает, что клиент отключился.

`server.py`

```python
import math
import socket

HOST = "127.0.0.1"
PORT = 8082


def solve(a, b, c):
    if a == 0:
        return "a = 0, уравнение не квадратное"
    d = b * b - 4 * a * c
    if d < 0:
        return f"D = {d:g}, действительных корней нет"
    if d == 0:
        x = -b / (2 * a) + 0.0
        return f"D = 0, x = {x:g}"
    x1 = (-b + math.sqrt(d)) / (2 * a)
    x2 = (-b - math.sqrt(d)) / (2 * a)
    return f"D = {d:g}, x1 = {x1:g}, x2 = {x2:g}"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"TCP-сервер запущен на {HOST}:{PORT}")

while True:
    conn, address = server.accept()
    print(f"Подключился {address}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                a, b, c = map(float, data.decode().split())
                answer = solve(a, b, c)
            except ValueError:
                answer = "Ошибка: нужно передать три числа"
            print(f"{data.decode()} -> {answer}")
            conn.sendall(answer.encode())
    except ConnectionError:
        pass
    conn.close()
    print(f"Отключился {address}")
```

`client.py`

```python
import socket

SERVER = ("127.0.0.1", 8082)


def read_number(name):
    while True:
        try:
            return float(input(f"{name} = "))
        except ValueError:
            print("Нужно ввести число")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(SERVER)
print("Решение квадратного уравнения ax^2 + bx + c = 0")

while True:
    a = read_number("a")
    b = read_number("b")
    c = read_number("c")
    client.sendall(f"{a} {b} {c}".encode())
    print("Ответ сервера:", client.recv(1024).decode())
    if input("Ещё раз? (y/n): ").lower() != "y":
        break

client.close()
```

Клиент:

```text
Решение квадратного уравнения ax^2 + bx + c = 0
a = 1
b = -3
c = 2
Ответ сервера: D = 1, x1 = 2, x2 = 1
Ещё раз? (y/n): y
a = 1
b = 2
c = 1
Ответ сервера: D = 0, x = -1
Ещё раз? (y/n): y
a = 1
b = 0
c = 4
Ответ сервера: D = -16, действительных корней нет
Ещё раз? (y/n): n
```

Сервер:

```text
TCP-сервер запущен на 127.0.0.1:8082
Подключился ('127.0.0.1', 49998)
1.0 -3.0 2.0 -> D = 1, x1 = 2, x2 = 1
1.0 2.0 1.0 -> D = 0, x = -1
1.0 0.0 4.0 -> D = -16, действительных корней нет
Отключился ('127.0.0.1', 49998)
```

## Задание 3. HTTP-сервер

Сервер в ответ на подключение клиента отправляет HTTP-сообщение с HTML-страницей из файла `index.html`.

HTTP работает поверх TCP, поэтому сервер устроен так же, как в задании 2. Ответ собирается вручную:
строка статуса, заголовки, пустая строка и тело. `Content-Length` считается в байтах, поэтому файл читается
как `bytes` — русская буква в UTF-8 занимает два байта. Клиентом служит браузер.

`server.py`

```python
import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8083
INDEX = Path(__file__).parent / "index.html"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"HTTP-сервер запущен: http://{HOST}:{PORT}/")

while True:
    conn, address = server.accept()
    conn.settimeout(5)
    try:
        request = conn.recv(1024).decode()
        if request:
            print(request.split("\r\n")[0])
            body = INDEX.read_bytes()
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            conn.sendall(headers.encode() + body)
    except OSError:
        pass
    conn.close()
```

`index.html`

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>ЛР1. Задание 3</title>
</head>
<body>
    <h1>Hello, client!</h1>
    <p>Эта страница отправлена сервером на сокетах.</p>
    <p>Павлов Виталий, K3339</p>
</body>
</html>
```

Ответ сервера:

```text
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 309
Connection: close

<!DOCTYPE html>
<html lang="ru">
...
```

В браузере по адресу <http://127.0.0.1:8083/> открывается страница из файла.

## Задание 4. Многопользовательский чат

Реализовать многопользовательский чат с использованием `socket` и `threading`. Выбран протокол TCP.

Главный поток сервера только принимает подключения. Для каждого клиента запускается поток `handle_client`,
который сначала спрашивает имя, а затем пересылает сообщения клиента всем остальным. Подключённые
пользователи хранятся в словаре «сокет → имя». Словарь меняют несколько потоков, поэтому доступ к нему
закрыт блокировкой `Lock`. Имена не повторяются, по ним пользователей можно различить.

Клиент один, его запускают в нескольких терминалах. В нём два потока: главный читает ввод и отправляет
его на сервер, второй принимает сообщения и печатает их. Без второго потока клиент не видел бы чужих
сообщений, пока ждёт ввода в `input`. Выход — команда `/quit`: клиент закрывает сокет, сервер получает
пустой `recv` и сообщает остальным, что пользователь вышел.

`server.py`

```python
import socket
import threading

HOST = "127.0.0.1"
PORT = 8084

clients = {}
lock = threading.Lock()


def broadcast(text, sender=None):
    with lock:
        for conn in clients:
            if conn is not sender:
                try:
                    conn.sendall(text.encode())
                except OSError:
                    pass


def handle_client(conn, address):
    name = None
    try:
        conn.sendall("Введите имя:\n".encode())
        while name is None:
            data = conn.recv(1024)
            if not data:
                return
            new_name = data.decode().strip()
            with lock:
                if new_name not in clients.values():
                    clients[conn] = new_name
                    name = new_name
            if name is None:
                conn.sendall("Имя занято, введите другое:\n".encode())

        print(f"{address} вошёл как {name}")
        conn.sendall("Вы в чате. Для выхода введите /quit\n".encode())
        broadcast(f"{name} вошёл в чат\n", conn)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = f"{name}: {data.decode().strip()}"
            print(message)
            broadcast(message + "\n", conn)
    except OSError:
        pass
    finally:
        with lock:
            clients.pop(conn, None)
        conn.close()
        if name is not None:
            print(f"{name} вышел")
            broadcast(f"{name} вышел из чата\n")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Сервер чата запущен на {HOST}:{PORT}")

while True:
    conn, address = server.accept()
    threading.Thread(target=handle_client, args=(conn, address), daemon=True).start()
```

`client.py`

```python
import socket
import threading

SERVER = ("127.0.0.1", 8084)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(SERVER)


def receive():
    while True:
        try:
            data = client.recv(1024)
        except OSError:
            break
        if not data:
            print("Сервер закрыл соединение")
            break
        print(data.decode(), end="")


threading.Thread(target=receive, daemon=True).start()

try:
    while True:
        text = input().strip()
        if text == "/quit":
            break
        if text:
            client.sendall(text.encode())
except (KeyboardInterrupt, OSError):
    pass

client.close()
print("Вы вышли из чата")
```

Запущены сервер и три клиента. Третий клиент сначала ввёл занятое имя.

Vitaly:

```text
Введите имя:
Vitaly
Вы в чате. Для выхода введите /quit
Masha вошёл в чат
Petya вошёл в чат
Всем привет!
Masha: Привет, Виталий
Petya: Я тоже тут
/quit
Вы вышли из чата
```

Petya:

```text
Введите имя:
Masha
Имя занято, введите другое:
Petya
Вы в чате. Для выхода введите /quit
Vitaly: Всем привет!
Masha: Привет, Виталий
Я тоже тут
Vitaly вышел из чата
Masha: Пока!
/quit
Вы вышли из чата
```

Сервер:

```text
Сервер чата запущен на 127.0.0.1:8084
('127.0.0.1', 50080) вошёл как Vitaly
('127.0.0.1', 50081) вошёл как Masha
('127.0.0.1', 50083) вошёл как Petya
Vitaly: Всем привет!
Masha: Привет, Виталий
Petya: Я тоже тут
Vitaly вышел
Masha: Пока!
Petya вышел
```

## Задание 5. Веб-сервер с GET и POST

Написать веб-сервер, который принимает и записывает информацию о дисциплине и оценке (POST) и отдаёт
HTML-страницу со всеми оценками (GET).

Сервер написан на основе базового класса из задания. Работа с запросом разбита на методы:

- `parse_request` — читает первую строку и достаёт из неё метод и путь;
- `parse_headers` — читает заголовки до пустой строки и складывает их в словарь;
- `handle_request` — по методу и пути выбирает, что ответить;
- `send_response` — отправляет строку статуса, заголовки и тело.

Тело POST-запроса читается ровно на столько байт, сколько указано в `Content-Length`. Форма приходит
в виде `discipline=...&grade=5`, она разбирается функцией `parse_qs`. Оценки хранятся в словаре
«дисциплина → список оценок», поэтому вторая оценка по тому же предмету попадает в уже существующий
список. При неверных данных сервер отвечает 400, на неизвестный путь — 404, на другие методы — 405.

`server.py`

```python
import html
import socket
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8085


class MyHTTPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.grades = {}

    def serve_forever(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        print(f"Сервер запущен: http://{self.host}:{self.port}/")
        while True:
            conn, address = server.accept()
            try:
                self.serve_client(conn)
            except (OSError, ValueError):
                pass
            conn.close()

    def serve_client(self, conn):
        conn.settimeout(5)
        rfile = conn.makefile("rb")
        method, path = self.parse_request(rfile)
        headers = self.parse_headers(rfile)
        length = int(headers.get("content-length", 0))
        body = rfile.read(length).decode()
        print(method, path)
        self.handle_request(conn, method, path, body)

    def parse_request(self, rfile):
        line = rfile.readline().decode()
        method, path, version = line.split()
        return method, path

    def parse_headers(self, rfile):
        headers = {}
        while True:
            line = rfile.readline().decode().strip()
            if not line:
                break
            name, value = line.split(":", 1)
            headers[name.lower()] = value.strip()
        return headers

    def handle_request(self, conn, method, path, body):
        if path != "/":
            self.send_response(conn, 404, "Not Found", "<h1>404 Not Found</h1>")
        elif method == "GET":
            self.send_response(conn, 200, "OK", self.render_page())
        elif method == "POST":
            form = parse_qs(body)
            discipline = form.get("discipline", [""])[0].strip()
            grade = form.get("grade", [""])[0]
            if not discipline or grade not in ("1", "2", "3", "4", "5"):
                self.send_response(conn, 400, "Bad Request", "<h1>400 Bad Request</h1>")
                return
            if discipline not in self.grades:
                self.grades[discipline] = []
            self.grades[discipline].append(int(grade))
            self.send_response(conn, 200, "OK", self.render_page())
        else:
            self.send_response(conn, 405, "Method Not Allowed", "<h1>405 Method Not Allowed</h1>")

    def send_response(self, conn, status, reason, body):
        body = body.encode()
        headers = (
            f"HTTP/1.1 {status} {reason}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        conn.sendall(headers.encode() + body)

    def render_page(self):
        rows = ""
        for discipline, grades in self.grades.items():
            marks = ", ".join(map(str, grades))
            rows += f"<tr><td>{html.escape(discipline)}</td><td>{marks}</td></tr>"
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <form method="POST" action="/">
        <input name="discipline" placeholder="Дисциплина" required>
        <input name="grade" type="number" min="1" max="5" placeholder="Оценка" required>
        <button type="submit">Добавить</button>
    </form>
    <table border="1" cellpadding="6">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
</body>
</html>"""


if __name__ == "__main__":
    MyHTTPServer(HOST, PORT).serve_forever()
```

После добавления оценок 5 и 4 по математике и 5 по веб-программированию страница выглядит так:

| Дисциплина | Оценки |
|---|---|
| Математика | 5, 4 |
| Web-программирование | 5 |

Проверка через `curl`:

```text
$ curl -i -d "discipline=Math&grade=5" http://127.0.0.1:8085/
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 795
Connection: close
```

Сервер:

```text
Сервер запущен: http://127.0.0.1:8085/
GET /
POST /
POST /
GET /
```

## Вывод

В ходе работы реализованы клиент и сервер на UDP и TCP, HTTP-сервер, отдающий страницу из файла,
многопользовательский чат на потоках и веб-сервер с обработкой GET и POST. Стало понятно, чем UDP
отличается от TCP на уровне кода и что HTTP — это текстовый протокол поверх TCP, запросы и ответы
которого можно разбирать и собирать вручную.

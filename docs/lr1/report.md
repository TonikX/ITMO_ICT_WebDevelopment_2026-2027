# Лабораторная работа №1. Работа с сокетами

Выполнил: Артемов Илья, группа K3341. Вариант практического задания 2: 1 (теорема Пифагора).

## Цель работы

Понять принципы межсокетного взаимодействия в вебе. Научиться реализовывать базовую архитектуру клиент-сервер.

## Практическое задание 1. Обмен сообщениями по UDP

Задача: Реализовать клиентскую и серверную часть приложения. Клиент отправляет серверу сообщение «Hello, server», и оно должно отобразиться на стороне сервера. В ответ сервер отправляет клиенту сообщение «Hello, client», которое должно отобразиться у клиента. Использовать библиотеку `socket` и протокол UDP.

### Описание протокола

UDP - протокол без установления соединения: отправитель посылает датаграмму, не дожидаясь подтверждения от получателя.

1. Сервер создаёт сокет `socket(AF_INET, SOCK_DGRAM)`, привязывает его к адресу `localhost:9001` (`bind`) и ждёт датаграммы в `recvfrom()`.
2. Клиент отправляет датаграмму с текстом `Hello, server` на адрес сервера (`sendto`).
3. `recvfrom()` на сервере возвращает данные и адрес клиента. Сервер выводит сообщение и отправляет на этот адрес датаграмму `Hello, client`.
4. Клиент получает ответ (`recvfrom`) и выводит его.

### Код сервера

```python
import socket

HOST = "localhost"
PORT = 9001

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print(f"UDP-сервер запущен на {HOST}:{PORT}")

try:
    while True:
        data, client_address = server_socket.recvfrom(1024)
        print(f"Сообщение от клиента {client_address}: {data.decode()}")

        server_socket.sendto("Hello, client".encode(), client_address)
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()
```

### Код клиента

```python
import socket

HOST = "localhost"
PORT = 9001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto("Hello, server".encode(), (HOST, PORT))

data, server_address = client_socket.recvfrom(1024)
print(f"Сообщение от сервера: {data.decode()}")

client_socket.close()
```

### Пример работы

Терминал сервера:

```text
$ python3 task1_udp/server.py
UDP-сервер запущен на localhost:9001
Сообщение от клиента ('127.0.0.1', 56198): Hello, server
```

Терминал клиента:

```text
$ python3 task1_udp/client.py
Сообщение от сервера: Hello, client
```

## Практическое задание 2. Вычисления через TCP

Задача: Реализовать клиентскую и серверную часть приложения. Клиент запрашивает выполнение математической операции, параметры которой вводятся с клавиатуры. Сервер обрабатывает данные и возвращает результат клиенту. Использовать библиотеку `socket` и протокол TCP.

Вариант 1 - теорема Пифагора: в прямоугольном треугольнике квадрат гипотенузы равен сумме квадратов катетов, c² = a² + b². Клиент вводит катеты a и b, сервер вычисляет гипотенузу c = √(a² + b²).

### Описание протокола

TCP требует установления соединения перед обменом данными и гарантирует доставку и порядок байт.

1. Сервер создаёт сокет `socket(AF_INET, SOCK_STREAM)`, привязывает его к адресу `localhost:9002` и ждёт подключений (`listen`, `accept`).
2. Клиент запрашивает у пользователя длины катетов, подключается к серверу (`connect`) и отправляет их одной строкой через пробел, например `3 4`.
3. Сервер вычисляет гипотенузу и отправляет клиенту строку с результатом. Если пришли не два положительных числа, сервер отправляет сообщение об ошибке.
4. Клиент выводит ответ, после чего соединение закрывается.

### Код сервера

```python
import math
import socket

HOST = "localhost"
PORT = 9002

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"TCP-сервер запущен на {HOST}:{PORT}")

try:
    while True:
        client_connection, client_address = server_socket.accept()
        print(f"Подключение от {client_address}")

        request = client_connection.recv(1024).decode()
        print(f"Запрос от клиента: {request}")

        try:
            a, b = map(float, request.split())
            if a <= 0 or b <= 0:
                raise ValueError
            response = f"Гипотенуза c = {math.hypot(a, b)}"
        except ValueError:
            response = "Ошибка: нужно ввести два положительных числа - длины катетов"

        client_connection.sendall(response.encode())
        client_connection.close()
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()
```

### Код клиента

```python
import socket

HOST = "localhost"
PORT = 9002

print("Теорема Пифагора: вычисление гипотенузы по двум катетам")
a = input("Введите катет a: ")
b = input("Введите катет b: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.sendall(f"{a} {b}".encode())

response = client_socket.recv(1024).decode()
print(f"Ответ от сервера: {response}")

client_socket.close()
```

### Пример работы

Терминал сервера:

```text
$ python3 task2_tcp/server.py
TCP-сервер запущен на localhost:9002
Подключение от ('127.0.0.1', 52226)
Запрос от клиента: 3 4
Подключение от ('127.0.0.1', 52227)
Запрос от клиента: -3 4
```

Терминал клиента — вычисление гипотенузы по катетам 3 и 4:

```text
$ python3 task2_tcp/client.py
Теорема Пифагора: вычисление гипотенузы по двум катетам
Введите катет a: 3
Введите катет b: 4
Ответ от сервера: Гипотенуза c = 5.0
```

Терминал клиента — некорректные данные:

```text
$ python3 task2_tcp/client.py
Теорема Пифагора: вычисление гипотенузы по двум катетам
Введите катет a: -3
Введите катет b: 4
Ответ от сервера: Ошибка: нужно ввести два положительных числа - длины катетов
```

## Практическое задание 3. Раздача HTML-страницы по HTTP

Задача: Реализовать серверную часть приложения. Клиент подключается к серверу и в ответ получает HTTP-сообщение, содержащее HTML-страницу, которую сервер подгружает из файла `index.html`. Использовать библиотеку `socket`.

### Описание протокола

HTTP работает поверх TCP. HTTP-ответ - это текст строгого формата: строка статуса, заголовки, пустая строка и тело.

1. Сервер ждёт подключения на `localhost:9003`. Клиент (браузер или `curl`) подключается и отправляет HTTP-запрос, например `GET / HTTP/1.1` с заголовками.
2. Сервер читает запрос до пустой строки (`\r\n\r\n`), которой заканчиваются заголовки.
3. Сервер читает файл `index.html` и формирует ответ: строку статуса `HTTP/1.1 200 OK`, заголовки `Content-Type`, `Content-Length` (длина тела в байтах) и `Connection: close`, пустую строку и содержимое файла.
4. Ответ отправляется через тот же сокет, который принял подключение (`sendall`), после чего соединение закрывается.

### Код сервера

```python
import socket
from pathlib import Path

HOST = "localhost"
PORT = 9003
INDEX_FILE = Path(__file__).with_name("index.html")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"HTTP-сервер запущен: http://{HOST}:{PORT}/")

try:
    while True:
        client_connection, client_address = server_socket.accept()

        request = b""
        while b"\r\n\r\n" not in request:
            chunk = client_connection.recv(1024)
            if not chunk:
                break
            request += chunk

        if request:
            request_line = request.split(b"\r\n")[0].decode()
            print(f"Запрос от {client_address}: {request_line}")

            body = INDEX_FILE.read_bytes()

            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode() + body
            client_connection.sendall(http_response)

        client_connection.close()
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()
```

### Файл index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Практическое задание 3</title>
</head>
<body>
    <h1>Привет! Это HTML-страница из файла index.html</h1>
    <p>Страницу отправил сервер, написанный на Python с помощью библиотеки socket.</p>
</body>
</html>
```

### Пример работы

Терминал сервера:

```text
$ python3 task3_http/server.py
HTTP-сервер запущен: http://localhost:9003/
Запрос от ('127.0.0.1', 52229): GET / HTTP/1.1
```

Терминал клиента - запрос утилитой `curl` (параметр `-i` выводит строку статуса и заголовки ответа). Эту же страницу можно открыть в браузере по адресу `http://localhost:9003/`.

```text
$ curl -i http://localhost:9003/
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 381
Connection: close

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Практическое задание 3</title>
</head>
<body>
    <h1>Привет! Это HTML-страница из файла index.html</h1>
    <p>Страницу отправил сервер, написанный на Python с помощью библиотеки socket.</p>
</body>
</html>
```

## Практическое задание 4. Чат на сокетах

Задача: Реализовать многопользовательский чат. Использовать библиотеки `socket` и `threading`. Должна быть возможность идентифицировать пользователей, пользователь должен иметь возможность выйти из чата. Реализация выполнена на протоколе TCP.

### Описание протокола

Сообщения передаются по TCP в виде строк текста в кодировке UTF-8, каждая строка заканчивается символом `\n`.

1. Сервер ждёт подключений на `localhost:9004`. Для каждого подключившегося пользователя запускается отдельный поток (`threading.Thread`).
2. Клиент - один скрипт `client.py`, который каждый пользователь запускает в своём терминале. При запуске пользователь вводит имя, и клиент отправляет его серверу первой строкой.
3. Сервер сохраняет пользователя в словаре `clients` (сокет → имя). Словарь защищён блокировкой `threading.Lock`, потому что с ним работают потоки всех пользователей.
4. Каждая следующая строка от клиента - сообщение. Сервер рассылает его всем пользователям, кроме отправителя, в виде `имя: текст`. По имени пользователя идентифицируют.
5. Для выхода пользователь вводит `/exit`. Сервер удаляет пользователя из словаря и закрывает соединение.
6. На клиенте сообщения от сервера принимает отдельный поток, поэтому они выводятся сразу, пока основной поток ждёт ввода с клавиатуры.

### Код сервера

```python
import socket
import threading

HOST = "localhost"
PORT = 9004

clients = {}
clients_lock = threading.Lock()


def broadcast(message, sender):
    with clients_lock:
        for client_socket in clients:
            if client_socket is not sender:
                try:
                    client_socket.sendall(message.encode())
                except OSError:
                    pass


def handle_client(client_socket, client_address):
    reader = client_socket.makefile("r", encoding="utf-8")
    name = ""
    try:
        name = reader.readline().strip()
        if not name:
            return
        with clients_lock:
            clients[client_socket] = name
        print(f"{name} вошёл в чат {client_address}")

        for line in reader:
            message = line.strip()
            if message == "/exit":
                break
            print(f"{name}: {message}")
            broadcast(f"{name}: {message}\n", client_socket)
    except OSError:
        pass
    finally:
        with clients_lock:
            clients.pop(client_socket, None)
        reader.close()
        client_socket.close()
        if name:
            print(f"{name} вышел из чата")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Сервер чата запущен на {HOST}:{PORT}")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True).start()
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()
```

### Код клиента

```python
import socket
import threading

HOST = "localhost"
PORT = 9004


def receive_messages(client_socket):
    try:
        for line in client_socket.makefile("r", encoding="utf-8"):
            print(line, end="")
    except OSError:
        pass


name = ""
while not name:
    name = input("Введите ваше имя: ").strip()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.sendall(f"{name}\n".encode())
print("Вы вошли в чат. Для выхода введите /exit")

threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

try:
    while True:
        message = input().strip()
        if not message:
            continue
        client_socket.sendall(f"{message}\n".encode())
        if message == "/exit":
            break
except (EOFError, KeyboardInterrupt, OSError):
    pass

client_socket.close()
print("Вы вышли из чата")
```

### Пример работы

Сервер и три пользователя, каждый в своём терминале. Alice, Bob и Carol обмениваются сообщениями, затем Bob, Alice и Carol по очереди выходят из чата командой `/exit`.

Терминал сервера:

```text
$ python3 task4_chat/server.py
Сервер чата запущен на localhost:9004
Alice вошёл в чат ('127.0.0.1', 52276)
Bob вошёл в чат ('127.0.0.1', 52278)
Carol вошёл в чат ('127.0.0.1', 52279)
Alice: Всем привет!
Bob: Привет, Alice!
Carol: Привет всем!
Bob вышел из чата
Alice: Carol, Bob вышел
Alice вышел из чата
Carol вышел из чата
```

Терминал Alice:

```text
$ python3 task4_chat/client.py
Введите ваше имя: Alice
Вы вошли в чат. Для выхода введите /exit
Всем привет!
Bob: Привет, Alice!
Carol: Привет всем!
Carol, Bob вышел
/exit
Вы вышли из чата
```

Терминал Bob:

```text
$ python3 task4_chat/client.py
Введите ваше имя: Bob
Вы вошли в чат. Для выхода введите /exit
Alice: Всем привет!
Привет, Alice!
Carol: Привет всем!
/exit
Вы вышли из чата
```

Терминал Carol:

```text
$ python3 task4_chat/client.py
Введите ваше имя: Carol
Вы вошли в чат. Для выхода введите /exit
Alice: Всем привет!
Bob: Привет, Alice!
Привет всем!
Alice: Carol, Bob вышел
/exit
Вы вышли из чата
```

## Практическое задание 5. Простой веб-сервер (GET/POST)

Задача: Написать простой веб-сервер для обработки GET и POST HTTP-запросов с помощью библиотеки `socket`. Сервер должен принимать и записывать информацию о дисциплине и оценке по дисциплине, а также отдавать информацию обо всех оценках по дисциплинам в виде HTML-страницы.

### Хранение оценок

Оценки хранятся в словаре, где ключ - название дисциплины, а значение - список её оценок:

```python
journal = {"Математика": ["5", "4"], "Физика": ["3"]}
```

Так каждой дисциплине соответствует одна запись, а новая оценка добавляется в список уже существующей дисциплины: `journal.setdefault(discipline, []).append(grade)`.

### Описание протокола

HTTP-запрос разбирается вручную:

1. Из сокета читаются данные до пустой строки (`\r\n\r\n`), которой заканчиваются заголовки.
2. Из первой строки запроса (например, `POST / HTTP/1.1`) определяются метод и путь.
3. Для POST из заголовка `Content-Length` берётся длина тела, и тело дочитывается из сокета до этой длины.

По методу сервер решает, что делать:

| Метод | Путь | Действие |
|-------|------|----------|
| GET | `/` | вернуть HTML-страницу со всеми оценками и формой добавления оценки |
| POST | `/` | сохранить оценку из тела запроса `discipline=...&grade=...` и вернуть HTML-страницу с оценками |

Тело POST-запроса формы имеет вид `discipline=%D0%A4%D0%B8%D0%B7%D0%B8%D0%BA%D0%B0&grade=5`: значения кодируются, их раскодирует функция `parse_qs`. Если дисциплина или оценка не указана, сервер отвечает `400 Bad Request`, на другой путь - `404 Not Found`, на другой метод - `501 Not Implemented`.

### Код сервера

```python
import html
import socket
from urllib.parse import parse_qs

HOST = "localhost"
PORT = 9005

journal = {}


def read_request(client_connection):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = client_connection.recv(1024)
        if not chunk:
            return None
        data += chunk
    head, body = data.split(b"\r\n\r\n", 1)
    lines = head.decode().split("\r\n")

    method, path, _ = lines[0].split(" ")

    content_length = 0
    for line in lines[1:]:
        header_name, header_value = line.split(":", 1)
        if header_name.strip().lower() == "content-length":
            content_length = int(header_value)

    while len(body) < content_length:
        chunk = client_connection.recv(1024)
        if not chunk:
            break
        body += chunk
    return method, path, body.decode()


def journal_page():
    rows = ""
    for discipline, grades in journal.items():
        rows += f"        <tr><td>{html.escape(discipline)}</td><td>{html.escape(', '.join(grades))}</td></tr>\n"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <table border="1">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
{rows}    </table>
    <h2>Добавить оценку</h2>
    <form method="post" action="/">
        <p>Дисциплина: <input name="discipline" required></p>
        <p>Оценка: <input name="grade" required></p>
        <button type="submit">Сохранить</button>
    </form>
</body>
</html>
"""


def send_response(client_connection, status, body):
    body = body.encode()
    head = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    client_connection.sendall(head.encode() + body)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Веб-сервер запущен: http://{HOST}:{PORT}/")

try:
    while True:
        client_connection, client_address = server_socket.accept()
        request = read_request(client_connection)

        if request:
            method, path, body = request
            print(f"{method} {path} от {client_address}")

            if path != "/":
                send_response(client_connection, "404 Not Found", "<h1>404 Not Found</h1>")
            elif method == "GET":
                send_response(client_connection, "200 OK", journal_page())
            elif method == "POST":
                form = parse_qs(body)
                discipline = form.get("discipline", [""])[0].strip()
                grade = form.get("grade", [""])[0].strip()
                if discipline and grade:
                    journal.setdefault(discipline, []).append(grade)
                    print(f"Записана оценка: {discipline} — {grade}")
                    send_response(client_connection, "200 OK", journal_page())
                else:
                    send_response(client_connection, "400 Bad Request", "<h1>Нужно указать дисциплину и оценку</h1>")
            else:
                send_response(client_connection, "501 Not Implemented", "<h1>Поддерживаются только GET и POST</h1>")

        client_connection.close()
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()
```

### Пример работы

Сервер запускается, затем оценки отправляются POST-запросами. Утилита `curl` с параметром `-d` отправляет POST-запрос с телом формы, параметр `-o /dev/null` скрывает возвращаемую страницу. Затем GET-запросом запрашивается страница с оценками. В браузере та же страница открывается по адресу `http://localhost:9005/`, оценки добавляются через форму на ней.

Терминал клиента:

```text
$ curl -o /dev/null -s -d "discipline=Математика&grade=5" http://localhost:9005/
$ curl -o /dev/null -s -d "discipline=Математика&grade=4" http://localhost:9005/
$ curl -o /dev/null -s -d "discipline=Физика&grade=3" http://localhost:9005/
$ curl -i http://localhost:9005/
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 675
Connection: close

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <table border="1">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        <tr><td>Математика</td><td>5, 4</td></tr>
        <tr><td>Физика</td><td>3</td></tr>
    </table>
    <h2>Добавить оценку</h2>
    <form method="post" action="/">
        <p>Дисциплина: <input name="discipline" required></p>
        <p>Оценка: <input name="grade" required></p>
        <button type="submit">Сохранить</button>
    </form>
</body>
</html>
```

Две оценки по математике попали в одну запись «Математика» со списком оценок `5, 4`.

Терминал сервера:

```text
$ python3 task5_web_server/server.py
Веб-сервер запущен: http://localhost:9005/
POST / от ('127.0.0.1', 52285)
Записана оценка: Математика — 5
POST / от ('127.0.0.1', 52287)
Записана оценка: Математика — 4
POST / от ('127.0.0.1', 52289)
Записана оценка: Физика — 3
GET / от ('127.0.0.1', 52291)
```

## Вывод

В ходе работы изучено взаимодействие клиента и сервера через сокеты. Реализованы обмен сообщениями по UDP, вычисление по теореме Пифагора по TCP, раздача HTML-страницы по HTTP, многопользовательский чат на TCP с потоками и веб-сервер, обрабатывающий GET- и POST-запросы и хранящий оценки, сгруппированные по дисциплинам.

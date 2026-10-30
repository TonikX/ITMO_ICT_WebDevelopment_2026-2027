# Лабораторная работа №1. Сокеты и клиент-серверное взаимодействие

## Цель работы

Цель работы — понять принципы межсокетного взаимодейсвтия в вебе. Научиться реализовывать базовую архитектуру клиент-сервер.

## Практическое задание 1. Обмен сообщениями по UDP

В первом задании нужно было реализовать клиентскую и серверную части приложения с использованием протокола UDP.

Клиент должен отправить серверу сообщение:

`Hello, server`

Сервер получает это сообщение, выводит его и отправляет клиенту ответ:

`Hello, client`

Для работы с UDP используется:

```python
socket.SOCK_DGRAM
```

### Сервер

```python
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("127.0.0.1", 8080))

data, client_address = server_socket.recvfrom(1024)

print(data.decode("utf-8"))

ans = "Hello, client"

server_socket.sendto(
    ans.encode("utf-8"),
    client_address
)

server_socket.close()
```

Сначала создаётся UDP-сокет:

```python
socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
```

`AF_INET` означает использование IPv4, а `SOCK_DGRAM` — использование UDP.

Далее сервер привязывается к адресу `127.0.0.1` и порту `8080`:

```python
server_socket.bind(("127.0.0.1", 8080))
```

После этого сервер ожидает сообщение от клиента:

```python
data, client_address = server_socket.recvfrom(1024)
```

В переменной `data` находятся полученные данные, а в `client_address` — адрес клиента, которому потом нужно отправить ответ.

Полученные данные приходят в виде байтов, поэтому перед выводом они декодируются:

```python
data.decode("utf-8")
```

После получения сообщения сервер отправляет клиенту `Hello, client`.

### Клиент

```python
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "Hello, server"

client_socket.sendto(
    message.encode("utf-8"),
    ("127.0.0.1", 8080)
)

data, server_address = client_socket.recvfrom(1024)

print(data.decode("utf-8"))

client_socket.close()
```

Клиент также создаёт UDP-сокет.

Строка:

```python
message = "Hello, server"
```

преобразуется в байты и отправляется серверу с помощью `sendto()`.

После этого клиент ждёт ответ сервера:

```python
data, server_address = client_socket.recvfrom(1024)
```

### Вывод

После запуска сервера и клиента на стороне сервера выводится:

```text
Hello, server
```

На стороне клиента выводится:

```text
Hello, client
```

Таким образом, обмен сообщениями через UDP работает.

---

## Практическое задание 2. Вычисления через TCP


Во втором задании нужно было реализовать клиент-серверное приложение с использованием TCP.

Формула площади трапеции:

```text
S = (a + b) / 2 * h
```
Для TCP используется:

```python
socket.SOCK_STREAM
```

### Сервер

```python
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 8081))

server_socket.listen(1)

client_socket, client_address = server_socket.accept()

data = client_socket.recv(1024)

message = data.decode("utf-8")

a, b, h = map(float, message.split())

area = (a + b) / 2 * h

client_socket.sendall(
    str(area).encode("utf-8")
)

client_socket.close()
server_socket.close()
```

Сервер создаёт TCP-сокет и привязывается к адресу и порту.

Метод:

```python
server_socket.listen(1)
```

переводит сокет в режим ожидания подключений.

После этого:

```python
client_socket, client_address = server_socket.accept()
```

сервер принимает подключение клиента.

Далее сервер получает переданные данные:

```python
data = client_socket.recv(1024)
```

Клиент передаёт три числа одной строкой. На сервере строка разбивается на отдельные значения:

```python
a, b, h = map(float, message.split())
```

После этого вычисляется площадь трапеции:

```python
area = (a + b) / 2 * h
```

Полученный результат отправляется клиенту.

### Клиент

```python
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(("127.0.0.1", 8081))

a = float(input("Введите первое основание a: "))
b = float(input("Введите второе основание b: "))
h = float(input("Введите высоту h: "))

message = f"{a} {b} {h}"

client_socket.sendall(
    message.encode("utf-8")
)

data = client_socket.recv(1024)

print(
    "Площадь трапеции:",
    data.decode("utf-8")
)

client_socket.close()
```

На клиенте пользователь вводит параметры с клавиатуры.

Например:

```text
Введите первое основание a: 5
Введите второе основание b: 7
Введите высоту h: 4
```

Значения объединяются в одну строку:

```python
message = f"{a} {b} {h}"
```

и отправляются серверу.

После получения ответа клиент выводит результат.

### Вывод

Клиент передаёт параметры серверу, сервер выполняет вычисление и возвращает готовый результат.

---

## Практическое задание 3. Раздача HTML-страницы по HTTP

В третьем задании нужно было реализовать сервер, который возвращает клиенту HTML-страницу по HTTP.

HTML-код должен находиться в отдельном файле `index.html`.

Клиентом в данном случае является браузер

### Файл index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Лабораторная работа 1</title>
</head>
<body>
    <h1>Практическое задание 3</h1>

    <p>Раздача HTML-страницы по HTTP.</p>
</body>
</html>
```

### Сервер

```python
import socket

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind(
    ("127.0.0.1", 8082)
)

server_socket.listen(1)

client_socket, client_address = server_socket.accept()

request = client_socket.recv(1024)

with open(
    "index.html",
    "r",
    encoding="utf-8"
) as file:
    html = file.read()

body = html.encode("utf-8")

response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html\r\n"
    f"Content-Length: {len(body)}\r\n"
    "\r\n"
).encode("utf-8") + body

client_socket.sendall(response)

client_socket.close()
server_socket.close()
```

Сначала сервер создаёт TCP-сокет и ждёт подключения.
После подключения браузера сервер получает HTTP-запрос:

```python
request = client_socket.recv(1024)
```

Далее открывается файл `index.html`:

```python
with open("index.html", "r", encoding="utf-8") as file:
    html = file.read()
```

HTML преобразуется в байты:

```python
body = html.encode("utf-8")
```

После этого формируется HTTP-ответ.
```text
HTTP/1.1 200 OK
```

означает, что запрос успешно обработан.
Заголовок:

```text
Content-Type: text/html
```

сообщает браузеру, что передаётся HTML.
Заголовок:

```text
Content-Length
```

показывает длину тела ответа в байтах.
После HTTP-заголовков обязательно идёт пустая строка:

```python
"\r\n"
```

После неё передаётся само содержимое HTML-страницы.

### Вывод

В браузере отображается страница:

```text
Практическое задание 3

Раздача HTML-страницы по HTTP.
```

Cервер самостоятельно формирует HTTP-ответ и передает браузеру HTML-страницу из файла.

---

## Практическое задание 4. Многопользовательский чат


В четвёртом задании нужно было реализовать многопользовательский чат.
Для всех пользователей используется один файл `client.py`. Каждый пользователь просто запускает этот файл в своём терминале.
При подключении пользователь вводит имя, по которому остальные участники чата могут его определить.


### Сервер

```python
import socket
import threading

HOST = "127.0.0.1"
PORT = 8083

clients = {}


def send_to_all(message, sender):
    for client in clients:
        if client != sender:
            client.sendall(
                message.encode("utf-8")
            )


def handle_client(client_socket):
    name = client_socket.recv(1024).decode("utf-8")

    clients[client_socket] = name

    print(name, "подключился")

    while True:
        message = client_socket.recv(1024).decode("utf-8")

        if message == "/exit" or not message:
            break

        print(name + ":", message)

        send_to_all(
            name + ": " + message,
            client_socket
        )

    del clients[client_socket]

    client_socket.close()

    print(name, "вышел из чата")


server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind((HOST, PORT))
server_socket.listen()

print("Сервер запущен")

while True:
    client_socket, address = server_socket.accept()

    thread = threading.Thread(
        target=handle_client,
        args=(client_socket,)
    )

    thread.start()
```

Все подключённые пользователи сохраняются в словаре:

```python
clients = {}
```

В качестве ключа используется сокет клиента, а в качестве значения — имя пользователя.

Например:

```python
{
    socket1: "Maria",
    socket2: "Anna"
}
```

Функция:

```python
send_to_all()
```

проходит по всем подключённым клиентам и отправляет им сообщение.
Отправитель исключается из рассылки:

```python
if client != sender:
```

Для каждого подключившегося клиента создаётся отдельный поток:

```python
thread = threading.Thread(
    target=handle_client,
    args=(client_socket,)
)
```

Таким образом сервер может одновременно принимать сообщения от разных пользователей.

### Клиент

```python
import socket
import threading

HOST = "127.0.0.1"
PORT = 8083

client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client_socket.connect((HOST, PORT))

name = input("Введите имя: ")

client_socket.sendall(
    name.encode("utf-8")
)


def receive():
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                break

            print(message)

        except:
            break


thread = threading.Thread(
    target=receive
)

thread.start()

while True:
    message = input()

    client_socket.sendall(
        message.encode("utf-8")
    )

    if message == "/exit":
        break

client_socket.close()
```

На клиенте отдельный поток используется для получения сообщений.

Это нужно для того, чтобы программа одновременно могла:

- ждать сообщения от других пользователей;
- позволять текущему пользователю вводить свои сообщения.

Для выхода пользователь вводит:

```text
/exit
```

После этого цикл заканчивается и сокет закрывается.

### Вывод

Сообщения одного клиента передаются через сервер другим подключённым пользователям.

---

## Практическое задание 5. Простой веб-сервер GET/POST

### Описание задания

В пятом задании нужно было реализовать простой HTTP-сервер с помощью библиотеки `socket`.

Сервер должен самостоятельно:

- разобрать HTTP-запрос;
- определить метод GET или POST;
- получить путь запроса;
- прочитать HTTP-заголовки;
- для POST прочитать тело запроса;
- сохранить дисциплину и оценку;
- для GET вернуть HTML-страницу с журналом оценок.

Оценки должны группироваться по предметам. Для хранения был выбран словарь:

```python
self.grades = {}
```

Например:

```python
{
    "Математика": ["5", "3"],
    "Физика": ["4"]
}
```

HTML-страница вынесена в отдельный файл `index.html`.

### Сервер

```python
import socket
from urllib.parse import urlparse, parse_qs


class MyHTTPServer:
    # Параметры сервера
    def __init__(self, host, port, server_name):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.grades = {}

    def serve_forever(self):
        # 1. Запуск сервера на сокете, обработка входящих соединений
        server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen()

            print("Сервер запущен")

            while True:
                conn, address = server_socket.accept()
                conn.settimeout(3)

                try:
                    self.serve_client(conn)
                except Exception as e:
                    print("Ошибка:", e)

        finally:
            server_socket.close()

    def serve_client(self, conn):
        # 2. Обработка клиентского подключения
        request = None

        try:
            request = self.parse_request(conn)

            if request is None:
                return

            response = self.handle_request(request)
            self.send_response(conn, response)

        except socket.timeout:
            pass

        except Exception as e:
            print("Ошибка при обработке клиента:", e)

        finally:
            if request:
                request["rfile"].close()

            conn.close()

    def parse_request(self, conn):
        # 3. Функция для обработки заголовка http+запроса.
        # Python, сокет предоставляет возможность создать вокруг него некоторую обертку,
        # которая предоставляет file object интерфейс. Это дает возможность построчно
        # обработать запрос. Заголовок всегда - первая строка. Первую строку нужно
        # разбить на 3 элемента (метод + url + версия протокола). URL необходимо
        # разбить на адрес и параметры.

        rfile = conn.makefile("rb")

        request_line = rfile.readline().decode("iso-8859-1").strip()

        if not request_line:
            return None

        method, target, version = request_line.split()

        url = urlparse(target)
        path = url.path
        params = parse_qs(url.query)

        headers = self.parse_headers(rfile)

        return {
            "method": method,
            "path": path,
            "params": params,
            "version": version,
            "headers": headers,
            "rfile": rfile
        }

    def parse_headers(self, rfile):
        # 4. Функция для обработки headers.
        # Необходимо прочитать все заголовки после первой строки
        # до появления пустой строки и сохранить их в массив.

        headers = {}

        while True:
            line = rfile.readline().decode("iso-8859-1")

            if line in ("\r\n", "\n", ""):
                break

            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

        return headers

    def handle_request(self, request):
        # 5. Функция для обработки url в соответствии с нужным методом.
        # В случае данной работы нужно будет создать набор условий,
        # который обрабатывает GET или POST запрос.
        # GET запрос должен возвращать данные.
        # POST запрос должен записывать данные на основе переданных параметров.

        method = request["method"]
        path = request["path"]

        if method == "GET" and path == "/grades":
            return self.handle_get()

        if method == "POST" and path == "/grades":
            return self.handle_post(request)

        return {
            "status": 404,
            "reason": "Not Found",
            "body": "Страница не найдена"
        }

    def handle_get(self):
        with open("index.html", "r", encoding="utf-8") as file:
            body = file.read()

        grades_html = ""

        if not self.grades:
            grades_html = "<p>Оценок пока нет</p>"
        else:
            grades_html = "<ul>"

            for subject, grades in self.grades.items():
                grades_html += (
                    f"<li><b>{subject}:</b> {', '.join(grades)}</li>"
                )

            grades_html += "</ul>"

        body = body.replace("{{grades}}", grades_html)

        return {
            "status": 200,
            "reason": "OK",
            "body": body
        }

    def handle_post(self, request):
        headers = request["headers"]
        rfile = request["rfile"]

        content_length = int(headers.get("Content-Length", 0))

        body = rfile.read(content_length).decode("utf-8")
        params = parse_qs(body)

        if "subject" not in params or "grade" not in params:
            return {
                "status": 400,
                "reason": "Bad Request",
                "body": "Не указана дисциплина или оценка"
            }

        subject = params["subject"][0]
        grade = params["grade"][0]

        if subject not in self.grades:
            self.grades[subject] = []

        self.grades[subject].append(grade)

        return self.handle_get()

    def send_response(self, conn, response):
        # 6. Функция для отправки ответа.
        # Необходимо записать в соединение status line вида
        # HTTP/1.1 <status_code> <reason>.
        # Затем построчно записать заголовки и пустую строку,
        # обозначающую конец секции заголовков.

        body = response["body"].encode("utf-8")

        status_line = (
            f'HTTP/1.1 {response["status"]} '
            f'{response["reason"]}\r\n'
        )

        headers = (
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        conn.sendall(
            status_line.encode("iso-8859-1")
            + headers.encode("iso-8859-1")
            + body
        )


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8084
    name = "localhost"

    serv = MyHTTPServer(host, port, name)

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
```

### Файл `index.html`

HTML-разметка страницы хранится отдельно от серверного кода.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 40px auto;
        }

        input {
            padding: 8px;
            margin-top: 5px;
        }

        button {
            padding: 10px 18px;
            margin-top: 15px;
        }

        li {
            margin-bottom: 10px;
        }
    </style>
</head>

<body>

    <h1>Журнал оценок</h1>

    <form method="POST" action="/grades">
        <p>
            <label>Дисциплина:</label><br>
            <input type="text" name="subject" required>
        </p>

        <p>
            <label>Оценка:</label><br>
            <input type="number" name="grade" min="1" max="5" required>
        </p>

        <button type="submit">Добавить оценку</button>
    </form>

    <h2>Все оценки</h2>

    {{grades}}

</body>
</html>
```

Вместо `{{grades}}` сервер подставляет сформированный список предметов и оценок:

```python
body = body.replace("{{grades}}", grades_html)
```

### Разбор HTTP-запроса

Первая строка HTTP-запроса может иметь вид:

```text
GET /grades HTTP/1.1
```

или:

```text
POST /grades HTTP/1.1
```

В методе:

```python
parse_request()
```

эта строка разбивается на три части:

```python
method, target, version = request_line.split()
```

Получаются:

- HTTP-метод;
- URL;
- версия протокола.

URL дополнительно разбирается с помощью:

```python
urlparse()
```

После первой строки сервер читает HTTP-заголовки.

Метод:

```python
parse_headers()
```

читает заголовки до появления пустой строки.

Если соединение было открыто, но HTTP-запрос не был передан, метод возвращает `None`:

```python
if not request_line:
    return None
```

### Обработка POST

При POST-запросе сервер читает тело запроса.

Размер тела определяется с помощью заголовка:

```text
Content-Length
```

```python
content_length = int(
    headers.get("Content-Length", 0)
)
```

После этого сервер читает указанное количество байт:

```python
body = rfile.read(content_length).decode("utf-8")
```

Например, тело запроса может иметь вид:

```text
subject=Математика&grade=5
```

С помощью:

```python
parse_qs(body)
```

оно разбирается на параметры.

Перед сохранением проверяется наличие дисциплины и оценки:

```python
if "subject" not in params or "grade" not in params:
    return {
        "status": 400,
        "reason": "Bad Request",
        "body": "Не указана дисциплина или оценка"
    }
```

Если предмет встречается первый раз:

```python
if subject not in self.grades:
    self.grades[subject] = []
```

для него создаётся новый список.

Затем оценка добавляется:

```python
self.grades[subject].append(grade)
```

За счёт этого несколько оценок одного предмета сохраняются вместе.

После добавления оценки вызывается:

```python
return self.handle_get()
```

поэтому браузер сразу отображает обновлённый журнал.

### Добавление оценок

Оценку можно добавить через форму в браузере или с помощью `curl`.

Например:

```bash
curl -X POST \
-d "subject=Математика&grade=5" \
http://127.0.0.1:8084/grades
```

Ещё одна оценка по тому же предмету:

```bash
curl -X POST \
-d "subject=Математика&grade=3" \
http://127.0.0.1:8084/grades
```

Оценка по другому предмету:

```bash
curl -X POST \
-d "subject=Физика&grade=4" \
http://127.0.0.1:8084/grades
```

После этого данные хранятся примерно так:

```python
{
    "Математика": ["5", "3"],
    "Физика": ["4"]
}
```

### Обработка GET

Для получения журнала используется запрос:

```text
GET /grades
```

При нём вызывается:

```python
handle_get()
```

Метод открывает файл `index.html`:

```python
with open("index.html", "r", encoding="utf-8") as file:
    body = file.read()
```

После этого сервер проходит по словарю оценок:

```python
for subject, grades in self.grades.items():
```

и формирует HTML-список.

Полученный список подставляется в страницу вместо:

```text
{{grades}}
```

### Результат

Для просмотра журнала в браузере открывается:

```text
http://127.0.0.1:8084/grades
```

Пользователь может ввести название дисциплины и оценку через форму.

Например, после добавления нескольких оценок на странице отображается:

```text
Журнал оценок

Все оценки

Математика: 5, 3
Физика: 4
```

Таким образом, сервер обрабатывает GET и POST запросы, сохраняет оценки в оперативной памяти и группирует их по дисциплинам, как требовалось в задании.

---

## Вывод

В ходе лабораторной работы я на практике разобралась с работой сокетов в Python и с основными принципами клиент-серверного взаимодействия.
Была рассмотрена работа двух транспортных протоколов — UDP и TCP. На практике стало понятно, что при работе с UDP данные можно отправлять без предварительного установления соединения, а при использовании TCP клиент сначала подключается к серверу.
Также я разобралась с базовой структурой HTTP-запроса и HTTP-ответа, научилась формировать HTTP-ответ вручную и обрабатывать GET и POST запросы.
Отдельно была рассмотрена работа сервера с несколькими клиентами одновременно с помощью `threading`.
В результате лабораторной работы я научилась создавать простые клиентские и серверные приложения с использованием библиотеки `socket` и лучше поняла, как происходит передача данных между клиентом и сервером.
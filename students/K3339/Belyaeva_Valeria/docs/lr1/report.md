# ЛР1. Работа с сокетами

**Студент:** Беляева Валерия, группа K3339

**Цель работы:** понять принципы взаимодействия через сокеты и реализовать базовую архитектуру клиент-сервер.

Все задания выполнены на Python с помощью стандартной библиотеки `socket`. Каждое задание лежит в своей папке, сервер и клиент запускаются в разных окнах терминала.

## Задание 1. Обмен сообщениями по UDP

UDP - протокол без установления соединения. Сокет создаётся с типом `SOCK_DGRAM`, сообщения отправляются через `sendto()` и принимаются через `recvfrom()`, который возвращает данные и адрес отправителя. По этому адресу сервер и отправляет ответ.

Сервер:

```python
import socket

# Создаем UDP сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 8081))
print("UDP сервер запущен на порту 8081...")

while True:
    data, addr = server_socket.recvfrom(1024)
    print(f"Получено от клиента: {data.decode('utf-8')}")
    # Отправляем ответ
    server_socket.sendto(b"Hello, client", addr)
```

Клиент:

```python
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 8081)

client_socket.sendto(b"Hello, server", server_address)
data, server = client_socket.recvfrom(1024)
print(f"Ответ сервера: {data.decode('utf-8')}")
client_socket.close()
```

Пример работы. Терминал сервера:

```
UDP сервер запущен на порту 8081...
Получено от клиента: Hello, server
```

Терминал клиента:

```
Ответ сервера: Hello, client
```

## Задание 2. Вычисления через TCP

Вариант 3: поиск площади трапеции.

TCP требует установить соединение: сервер вызывает `bind()`, `listen()` и ждёт клиента в `accept()`, клиент подключается через `connect()`. Клиент отправляет два основания и высоту одной строкой через запятую, сервер считает площадь по формуле `S = (a + b) / 2 * h` и возвращает результат. Если пришли не числа, сервер отвечает сообщением об ошибке.

Сервер:

```python
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Позволяет сразу перезапускать сервер на том же порту
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 8082))
server_socket.listen(1)
print("TCP сервер (площадь трапеции) запущен...")

while True:
    conn, addr = server_socket.accept()
    data = conn.recv(1024).decode('utf-8')
    if data:
        try:
            # Ожидаем три числа через запятую: "основание a,основание b,высота h"
            a, b, h = map(float, data.split(','))
            area = (a + b) / 2 * h
            conn.send(str(area).encode('utf-8'))
        except ValueError:
            conn.send("Ошибка: нужно ввести три числа".encode('utf-8'))
    conn.close()
```

Клиент:

```python
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8082))

a = input("Введите длину первого основания: ")
b = input("Введите длину второго основания: ")
h = input("Введите высоту: ")

client_socket.sendall(f"{a},{b},{h}".encode('utf-8'))
result = client_socket.recv(1024).decode('utf-8')
print(f"Площадь трапеции равна: {result}")
client_socket.close()
```

Пример работы клиента:

```
Введите длину первого основания: 4
Введите длину второго основания: 6
Введите высоту: 5
Площадь трапеции равна: 25.0
```

## Задание 3. Раздача HTML-страницы по HTTP

HTTP-ответ - это текст в строгом формате: строка статуса, заголовки, пустая строка и тело. Сервер читает `index.html` (путь берётся относительно самого скрипта, поэтому сервер можно запускать из любой папки), считает длину тела в байтах для заголовка `Content-Length` и отправляет всё через тот же сокет, который принял подключение. Если файла нет, возвращается статус 404.

Сервер:

```python
import os
import socket

# index.html лежит рядом со скриптом - так сервер работает из любой папки
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Позволяет сразу перезапускать сервер на том же порту
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 8083))
server_socket.listen(1)
print("HTTP сервер запущен на http://127.0.0.1:8083")

while True:
    conn, addr = server_socket.accept()
    request = conn.recv(1024)

    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
        status = "200 OK"
    except FileNotFoundError:
        html = "<h1>Error 404: index.html not found</h1>"
        status = "404 Not Found"

    # Формируем HTTP-ответ
    response = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html.encode('utf-8'))}\r\n"
        "Connection: close\r\n\r\n"
        f"{html}"
    )

    conn.sendall(response.encode('utf-8'))
    conn.close()
```

Страница `index.html`:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Лабораторная работа 1</title>
</head>
<body>
    <h1>Привет от сервера на сокетах!</h1>
    <p>Эта страница прочитана из файла index.html и отправлена по HTTP.</p>
</body>
</html>
```

Пример ответа сервера (запрос через `curl -i http://127.0.0.1:8083/`):

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 340
Connection: close

<!DOCTYPE html>
<html lang="ru">
...
```

## Задание 4. Многопользовательский чат

Чат реализован на TCP с потоками. Сервер хранит всех подключённых пользователей в словаре `clients` (сокет - имя). Для каждого подключения запускается отдельный поток `handle_client`: первым сообщением клиент присылает своё имя, дальше каждое сообщение рассылается всем остальным функцией `broadcast`.

Клиент один и тот же для всех пользователей: его запускают несколько раз в разных терминалах. Имя вводится при запуске, так пользователи идентифицируются. Отдельный поток на клиенте принимает сообщения, а основной читает ввод. Команда `exit` закрывает соединение, сервер это замечает и сообщает остальным о выходе.

Сервер:

```python
import socket
import threading

clients = {} # {socket: username}

def handle_client(conn, addr):
    # Первый пакет - имя пользователя
    name = conn.recv(1024).decode('utf-8')
    clients[conn] = name
    broadcast(f"--- {name} присоединился к чату ---", conn)

    while True:
        try:
            msg = conn.recv(1024).decode('utf-8')
            if not msg: break
            broadcast(f"[{name}]: {msg}", conn)
        except:
            break

    del clients[conn]
    conn.close()
    broadcast(f"--- {name} покинул чат ---", None)

def broadcast(message, sender_conn):
    # list() - копия, чтобы другой поток не изменил словарь во время обхода
    for c in list(clients):
        if c != sender_conn:
            try:
                c.send(message.encode('utf-8'))
            except:
                pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Позволяет сразу перезапускать сервер на том же порту
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 8084))
server.listen(5)
print("Чат-сервер запущен...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
```

Клиент:

```python
import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if not msg:
                print("Соединение с сервером потеряно.")
                break
            print(msg)
        except:
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8084))

name = input("Введите ваше имя: ")
client.send(name.encode('utf-8'))

# Запускаем поток для чтения входящих сообщений
threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

print("Вы в чате! Вводите сообщения (или 'exit' для выхода):")
while True:
    msg = input()
    if msg.lower() == 'exit':
        break
    if msg:
        client.send(msg.encode('utf-8'))

client.close()
```

Пример работы с тремя пользователями. Терминал Леры:

```
Введите ваше имя: Лера
Вы в чате! Вводите сообщения (или 'exit' для выхода):
--- Костя присоединился к чату ---
--- Соня присоединился к чату ---
Всем привет!
[Костя]: Привет, Лера
exit
```

Терминал Сони:

```
Введите ваше имя: Соня
Вы в чате! Вводите сообщения (или 'exit' для выхода):
[Лера]: Всем привет!
[Костя]: Привет, Лера
--- Лера покинул чат ---
--- Костя покинул чат ---
```

## Задание 5. Веб-сервер с GET и POST

Сервер вручную разбирает HTTP-запрос: по первой строке определяет метод, а для POST читает тело после пустой строки. Длина тела берётся из заголовка `Content-Length`, и если тело пришло не целиком, сервер дочитывает его из сокета.

Оценки хранятся в словаре `grades_journal`, где ключ - название дисциплины, а значение - список оценок. Поэтому несколько оценок по одному предмету попадают в одну запись, а не в отдельные строки. Перед вставкой в страницу текст проходит через `html.escape()`, чтобы введённые теги не выполнились как HTML.

- `GET /` - возвращает HTML-страницу с формой и журналом оценок.
- `POST /` - принимает поля `subject` и `grade`, добавляет оценку и возвращает обновлённую страницу.

Сервер:

```python
import html
import socket
import urllib.parse

# Хранилище: {'Математика': ['5', '4'], 'Физика': ['5']}
grades_journal = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Позволяет сразу перезапускать сервер на том же порту
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 8085))
server_socket.listen(1)
print("Сервер журнала запущен на http://127.0.0.1:8085")

def render_html():
    page = """
    <html><head><meta charset='utf-8'><title>Журнал оценок</title></head>
    <body>
        <h2>Добавить оценку</h2>
        <form method='POST'>
            <input type='text' name='subject' placeholder='Дисциплина' required>
            <input type='text' name='grade' placeholder='Оценка' required>
            <button type='submit'>Сохранить</button>
        </form>
        <h2>Журнал:</h2><ul>
    """
    for subject, grades in grades_journal.items():
        # html.escape - чтобы введённый текст не превратился в HTML-теги
        page += f"<li><b>{html.escape(subject)}</b>: {html.escape(', '.join(grades))}</li>"
    page += "</ul></body></html>"
    return page

while True:
    conn, addr = server_socket.accept()
    request = conn.recv(4096)

    if not request:
        conn.close()
        continue

    # Парсим HTTP-запрос: заголовки отделены от тела пустой строкой
    headers_part, _, body = request.partition(b'\r\n\r\n')
    lines = headers_part.decode('utf-8').split('\r\n')
    method = lines[0].split()[0]

    if method == 'POST':
        # Узнаем длину тела из заголовка Content-Length
        content_length = 0
        for line in lines[1:]:
            if line.lower().startswith('content-length:'):
                content_length = int(line.split(':')[1])

        # Браузер может прислать тело отдельным пакетом - дочитываем его
        while len(body) < content_length:
            body += conn.recv(4096)

        data = urllib.parse.parse_qs(body.decode('utf-8'))
        subject = data.get('subject', [''])[0].strip()
        grade = data.get('grade', [''])[0].strip()

        if subject and grade:
            if subject not in grades_journal:
                grades_journal[subject] = []
            grades_journal[subject].append(grade)

    html_content = render_html()
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(html_content.encode('utf-8'))}\r\n"
        "Connection: close\r\n\r\n"
        f"{html_content}"
    )

    conn.sendall(response.encode('utf-8'))
    conn.close()
```

Пример работы. После трёх запросов (Математика - 5, Физика - 4, Математика - 3) страница содержит:

```
Математика: 5, 3
Физика: 4
```

## Вывод

В работе реализованы клиент и сервер на UDP и TCP, отправка HTML-страницы по HTTP, многопользовательский чат на потоках и веб-сервер с обработкой GET и POST. На практике видно, чем отличаются протоколы: в UDP достаточно `sendto()` и `recvfrom()`, а в TCP нужно установить соединение, и для нескольких клиентов требуются потоки.

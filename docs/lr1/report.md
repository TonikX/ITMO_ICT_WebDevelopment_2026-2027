# ЛР1. Работа с сокетами

Титор Матвей, группа K3339, вариант 3.

## Задание 1. Обмен сообщениями по UDP

Клиент отправляет серверу сообщение `Hello, server`, сервер печатает его и отправляет в ответ `Hello, client`, клиент печатает ответ. UDP работает без установления соединения, поэтому на сервере нет `listen()` и `accept()`, а для отправки и приёма используются `sendto()` и `recvfrom()`.

### Сервер

```python
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind(('localhost', 9000))
print('Сервер запущен на порту 9000...')

while True:
    data, client_address = server_socket.recvfrom(1024)
    print(f'Получено от {client_address}: {data.decode()}')

    server_socket.sendto('Hello, client'.encode(), client_address)
    print(f'Отправлено {client_address}: Hello, client')
```

### Клиент

```python
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto('Hello, server'.encode(), ('localhost', 9000))
print('Отправлено серверу: Hello, server')

data, server_address = client_socket.recvfrom(1024)
print(f'Ответ от сервера: {data.decode()}')

client_socket.close()
```

### Работа в терминале

Сервер:

```text
Сервер запущен на порту 9000...
Получено от ('127.0.0.1', 56247): Hello, server
Отправлено ('127.0.0.1', 56247): Hello, client
```

Клиент:

```text
Отправлено серверу: Hello, server
Ответ от сервера: Hello, client
```

## Задание 2. Площадь трапеции по TCP (вариант 3)

Клиент вводит с клавиатуры два основания и высоту, отправляет их серверу одной строкой через точку с запятой: `a;b;h`. Сервер считает площадь по формуле `(a + b) / 2 * h` и возвращает результат. Если параметры введены неверно, сервер отправляет сообщение об ошибке и продолжает работать.

### Сервер

```python
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 9001))
server_socket.listen(1)
print('Сервер запущен на порту 9001 (площадь трапеции)...')

while True:
    connection, client_address = server_socket.accept()
    print(f'Соединение от {client_address}')

    request = connection.recv(1024).decode()
    print(f'Запрос от клиента: {request}')

    parts = request.strip().split(';')
    if len(parts) != 3:
        response = 'Ошибка: нужно три числа через точку с запятой (a;b;h)'
    else:
        try:
            a = float(parts[0].replace(',', '.'))
            b = float(parts[1].replace(',', '.'))
            h = float(parts[2].replace(',', '.'))
        except ValueError:
            response = 'Ошибка: параметры должны быть числами'
        else:
            if a <= 0 or b <= 0 or h <= 0:
                response = 'Ошибка: числа должны быть положительными'
            else:
                area = (a + b) / 2 * h
                response = f'Площадь трапеции: {area}'

    connection.sendall(response.encode())
    print(f'Ответ клиенту: {response}')
    connection.close()
```

### Клиент

```python
import socket

print('Вычисление площади трапеции: S = (a + b) / 2 * h')
a = input('Основание a: ')
b = input('Основание b: ')
h = input('Высота h: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9001))

client_socket.sendall(f'{a};{b};{h}'.encode())

response = client_socket.recv(1024).decode()
print(f'Результат: {response}')

client_socket.close()
```

### Работа в терминале

Клиент:

```text
Вычисление площади трапеции: S = (a + b) / 2 * h
Основание a: 3
Основание b: 5
Высота h: 4
Результат: Площадь трапеции: 16.0
```

Клиент при ошибочном вводе:

```text
Основание a: abc
Основание b: 5
Высота h: 4
Результат: Ошибка: параметры должны быть числами
```

Сервер:

```text
Сервер запущен на порту 9001 (площадь трапеции)...
Соединение от ('127.0.0.1', 59278)
Запрос от клиента: 3;5;4
Ответ клиенту: Площадь трапеции: 16.0
Соединение от ('127.0.0.1', 59280)
Запрос от клиента: abc;5;4
Ответ клиенту: Ошибка: параметры должны быть числами
```

## Задание 3. Раздача HTML-страницы по HTTP

Сервер при запуске читает файл `index.html` и отправляет его браузеру на любое подключение. Ответ формируется вручную: строка статуса `HTTP/1.1 200 OK`, заголовки `Content-Type` и `Content-Length`, пустая строка и сама страница. Страница читается в байтах, чтобы `Content-Length` был посчитан правильно.

### Сервер

```python
import socket

HOST = 'localhost'
PORT = 8080

with open('index.html', 'rb') as f:
    page = f.read()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'HTTP-сервер запущен: http://{HOST}:{PORT}/')

while True:
    connection, client_address = server_socket.accept()
    print(f'Подключение от {client_address}')

    request = connection.recv(1024).decode()
    print(f'Запрос: {request.splitlines()[0]}')

    headers = (
        'HTTP/1.1 200 OK\r\n'
        'Content-Type: text/html; charset=utf-8\r\n'
        f'Content-Length: {len(page)}\r\n'
        'Connection: close\r\n'
        '\r\n'
    )
    connection.sendall(headers.encode() + page)

    connection.close()
```

### Работа в терминале

Запрос через curl:

```text
$ curl -i http://localhost:8080/
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 477
Connection: close
```

Сервер:

```text
HTTP-сервер запущен: http://localhost:8080/
Подключение от ('127.0.0.1', 59657)
Запрос: GET / HTTP/1.1
```

## Задание 4. Многопользовательский чат (TCP + threading)

Первое сообщение клиента после подключения — его имя. Дальше клиент отправляет сообщения, сервер рассылает их всем остальным. Выйти можно командой `/exit` или просто закрыв терминал. На сервере для каждого клиента запускается отдельный поток, клиенты хранятся в словаре `{сокет: имя}`. Один и тот же `client.py` запускает каждый пользователь.

### Сервер

??? info "Полный код server.py"
    ```python
    import socket
    import threading

    HOST = 'localhost'
    PORT = 9002

    clients = {}
    clients_lock = threading.Lock()


    def broadcast(message, sender_conn=None):
        with clients_lock:
            recipients = [conn for conn in clients if conn != sender_conn]
        for conn in recipients:
            try:
                conn.sendall(message.encode())
            except OSError:
                remove_client(conn)


    def remove_client(conn):
        with clients_lock:
            name = clients.pop(conn, None)
        if name:
            print(f'[{name} покинул чат]')
        conn.close()


    def handle_client(conn, address):
        username = conn.recv(1024).decode()
        if not username:
            remove_client(conn)
            return

        with clients_lock:
            clients[conn] = username
        print(f'[{username} подключился из {address}]')
        broadcast(f'* {username} вошел в чат', conn)

        while True:
            try:
                data = conn.recv(1024)
            except ConnectionResetError:
                break
            if not data:
                break
            text = data.decode().strip()
            if text == '/exit':
                break
            if text:
                print(f'{username}: {text}')
                broadcast(f'{username}: {text}', conn)

        remove_client(conn)
        broadcast(f'* {username} покинул чат')


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Сервер чата запущен на {HOST}:{PORT}. Ожидание пользователей...')

    while True:
        conn, address = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, address), daemon=True).start()
    ```

### Клиент

??? info "Полный код client.py"
    ```python
    import socket
    import threading

    HOST = 'localhost'
    PORT = 9002


    def receive_messages(sock):
        while True:
            try:
                data = sock.recv(1024)
            except OSError:
                break
            if not data:
                print('\nСоединение с сервером разорвано')
                break
            print(f'\r{data.decode()}\n> ', end='', flush=True)


    username = input('Введите имя: ')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    client_socket.sendall(username.encode())
    print(f'Подключено к чату {HOST}:{PORT}. Команда /exit — выход.')

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        text = input('> ')
        if text.strip() == '/exit':
            client_socket.sendall(b'/exit')
            break
        if text:
            client_socket.sendall(text.encode())

    client_socket.close()
    print('Вы вышли из чата.')
    ```

### Работа в терминале

Сервер:

```text
Сервер чата запущен на localhost:9002. Ожидание пользователей...
[Alice подключился из ('127.0.0.1', 59675)]
[Bob подключился из ('127.0.0.1', 59677)]
Alice: Hi from Alice
Bob: Hi from Bob
[Alice покинул чат]
[Bob покинул чат]
```

Клиент Bob (видит сообщения Alice, своё сообщение ему не приходит):

```text
Введите имя: Bob
Подключено к чату localhost:9002. Команда /exit — выход.
> Alice: Hi from Alice
> /exit
Вы вышли из чата.
```

## Задание 5. Веб-сервер GET/POST

`GET /` — сервер отправляет HTML-страницу с формой и таблицей всех оценок. `POST /` — сервер разбирает тело формы (`discipline=...&grade=...`), сохраняет оценку и отправляет страницу обратно. Оценки хранятся в словаре `{дисциплина: [оценки]}` — одна запись на предмет со списком оценок. Неизвестный путь — 404, другой метод — 405.

### Сервер

??? info "Полный код server.py"
    ```python
    import socket
    from urllib.parse import parse_qs

    HOST = 'localhost'
    PORT = 8081

    grades = {}


    def read_request(conn):
        buffer = b''
        while b'\r\n\r\n' not in buffer:
            chunk = conn.recv(1024)
            if not chunk:
                raise ConnectionError
            buffer += chunk

        headers_part, _, body = buffer.partition(b'\r\n\r\n')
        lines = headers_part.decode().split('\r\n')

        method, path, version = lines[0].split(' ')

        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.lower()] = value.strip()

        content_length = int(headers.get('content-length', 0))
        while len(body) < content_length:
            chunk = conn.recv(1024)
            if not chunk:
                break
            body += chunk

        return method, path, body[:content_length]


    def make_response(status, body):
        body = body.encode()
        head = (
            f'HTTP/1.1 {status}\r\n'
            'Content-Type: text/html; charset=utf-8\r\n'
            f'Content-Length: {len(body)}\r\n'
            'Connection: close\r\n'
            '\r\n'
        )
        return head.encode() + body


    def build_page():
        rows = ''
        for discipline, marks in grades.items():
            marks_html = ''.join(f'<li>{mark}</li>' for mark in marks)
            rows += f'<tr><td>{discipline}</td><td><ul>{marks_html}</ul></td><td>{len(marks)}</td></tr>'

        if grades:
            table = f"<table border='1'><tr><th>Дисциплина</th><th>Оценки</th><th>Всего</th></tr>{rows}</table>"
        else:
            table = '<p>Журнал пуст — добавьте первую оценку.</p>'

        return f'''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Журнал оценок</title>
    </head>
    <body>
        <h1>Журнал оценок</h1>
        <form method="post" action="/">
            Дисциплина: <input name="discipline"><br><br>
            Оценка: <input name="grade"><br><br>
            <button type="submit">Добавить</button>
        </form>
        <h2>Оценки по дисциплинам</h2>
        {table}
    </body>
    </html>'''


    def handle_connection(conn, address):
        try:
            method, path, body = read_request(conn)
            print(f'{address}: {method} {path}')

            if path != '/':
                response = make_response('404 Not Found', '<h1>404 — страница не найдена</h1><p><a href="/">На главную</a></p>')
            elif method == 'GET':
                response = make_response('200 OK', build_page())
            elif method == 'POST':
                fields = parse_qs(body.decode())
                discipline = fields.get('discipline', [''])[0].strip()
                grade = fields.get('grade', [''])[0].strip()

                if discipline and grade:
                    grades.setdefault(discipline, []).append(grade)
                    print(f'Сохранено: {discipline} — {grade}')
                    response = make_response('200 OK', build_page())
                else:
                    response = make_response('200 OK', '<h1>Заполните оба поля</h1><p><a href="/">Вернуться</a></p>')
            else:
                response = make_response('405 Method Not Allowed', '<h1>Метод не поддерживается</h1>')

            conn.sendall(response)
        except ConnectionError:
            print(f'{address}: клиент отключился, не прислав запрос')
        finally:
            conn.close()


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Веб-сервер запущен: http://{HOST}:{PORT}/')

    while True:
        conn, address = server_socket.accept()
        handle_connection(conn, address)
    ```

### Работа в терминале

Добавление оценок:

```text
$ curl -d "discipline=Математика&grade=5" http://localhost:8081/
$ curl -d "discipline=Математика&grade=4" http://localhost:8081/
$ curl -d "discipline=Физика&grade=3" http://localhost:8081/
```

Сервер (оценки по одной дисциплине копятся в одну запись):

```text
Веб-сервер запущен: http://localhost:8081/
Сохранено: Математика — 5
Сохранено: Математика — 4
Сохранено: Физика — 3
```

Страница журнала после добавления:

```text
$ curl -s http://localhost:8081/
<tr><td>Математика</td><td><ul><li>5</li><li>4</li></ul></td><td>2</td></tr>
<tr><td>Физика</td><td><ul><li>3</li></ul></td><td>1</td></tr>
```

Неизвестный путь и метод:

```text
$ curl -o /dev/null -w "%{http_code}" http://localhost:8081/nope
404
$ curl -X PUT -o /dev/null -w "%{http_code}" http://localhost:8081/
405
```

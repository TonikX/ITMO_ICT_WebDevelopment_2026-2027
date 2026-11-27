# Задание 5 - Простой веб-сервер (GET/POST)

### Задача

Написать простой веб-сервер для обработки GET и POST HTTP-запросов с помощью
библиотеки `socket` в Python. Сервер должен:

- принимать и записывать информацию о дисциплине и оценке по дисциплине;
- отдавать информацию обо всех оценках по дисциплинам в виде HTML-страницы.

Журнал группируется по предмету: если для одной дисциплины пришло несколько оценок,
в хранилище должна быть одна запись с названием предмета и списком оценок.

### Теория

Сервер разбирает входящий запрос вручную: делит его по `\r\n\r\n` на заголовки и тело,
а по стартовой строке определяет метод.

- **GET** — сервер формирует HTML-страницу с таблицей «Дисциплина — Оценки» и
  возвращает её с кодом `200 OK`.
- **POST** — тело запроса имеет вид `Предмет : оценка`. Сервер добавляет оценку
  в словарь `marks` и отвечает кодом `201 Created`.

Для группировки по предмету используется словарь: ключ — название дисциплины,
значение — список оценок. Новая оценка по уже существующему предмету добавляется
в его список, а не создаёт отдельную запись.

Оценки хранятся в памяти процесса, поэтому после перезапуска сервера журнал пустой.

**Клиент** — консольное меню, которое формирует HTTP-запросы вручную:

1. просмотреть все оценки — отправляет GET-запрос и выводит полученный ответ;
2. добавить оценку — запрашивает предмет и оценку (допустимы значения 1–5)
   и отправляет POST-запрос;
3. выход.

Клиент держит одно соединение с сервером на протяжении всей работы, а сервер
обрабатывает запросы этого соединения в цикле, пока клиент не отключится.

### Код сервера

```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(('localhost', 45_000))
server.listen()

marks = dict()

def get(client):
    print('get')
    rows = ""
    for sub in marks:
        rows += f"<tr><td>{sub}</td><td>{marks[sub]}</td></tr>"
    html = f"""
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <title>Оценки по дисциплинам</title>
    </head>
    <body>
        <h1>Оценки по дисциплинам</h1>
        <table border="1" cellpadding="6">
            <tr><th>Дисциплина</th><th>Оценки</th></tr>
            {rows}
        </table>
    </body>
    </html>"""

    get_request_template = \
        f"""
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        Content-Length: {len(html.encode('utf-8'))}\r\n\r\n
        {html}
        """

    client.send(get_request_template.encode('utf-8'))
    print('get correct')


def post(body, client):
    print('post')
    post_request_template = \
        f"""
        HTTP/1.1 201 Created\r\n
        Content-Type: text/plain\r\n
        Content-Length: {len("1".encode('utf-8'))}\r\n\r\n
        1
        """
    buf = body.decode('utf-8').strip().split(' : ')
    if buf[0] in marks:
        marks[buf[0]].append(buf[1])
    else:
        marks[buf[0]] = [buf[1]]
    client.send(post_request_template.encode('utf-8'))
    print('post correct')


while True:
    client, address = server.accept()
    while True:
        raw_request = client.recv(4096)
        if not raw_request:
            break
        headers, _, body = raw_request.partition(b'\r\n\r\n')
        if b'GET' in headers.split(b'\r\n')[0]:
            get(client)
        elif b'POST' in headers.split(b'\r\n')[0]:
            post(body, client)
    client.close()
```

### Код клиента

```python
import socket
import os

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 45_000))

def get_marks(client):
    get_request_template = \
        """
        GET / HTTP/1.1\r\n
        Host: localhost\r\n\r\n
        """
    client.send(get_request_template.encode('utf-8'))
    response = client.recv(4096)
    print(response.decode('utf-8'))

def add_mark(client):
    subject = input('Введите предмет: ')
    mark = input('Введите оценку (1-5): ').strip()
    if mark not in ['1', '2', '3', '4', '5']:
        return
    body = f"{subject} : {mark}"
    post_request_template = \
        f"""
        POST / HTTP/1.1\r\n
        Host: localhost\r\n
        Content-Length: {len(body.encode('utf-8'))}\r\n\r\n
        {body}
        """
    print('send')
    client.send(post_request_template.encode('utf-8'))
    response = client.recv(4096)
    print(response.decode('utf-8'))

while True:
    os.system('clear')
    print('Журнал оценок')
    print('1. Просмотреть все оценки')
    print('2. Добавить новую оценку')
    print('0. Выход')
    inp = input('Введите цифру -> ')
    if inp == '0':
        break
    if inp == '1':
        get_marks(client)
        input()
    if inp == '2':
        add_mark(client)
        input()
```

### Запуск

Из папки `task5` в двух разных терминалах:

```bash
python3 server.py
```

```bash
python3 client.py
```

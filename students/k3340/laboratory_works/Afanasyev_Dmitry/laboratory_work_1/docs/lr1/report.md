# Лабораторная работа 1. Работа с сокетами

Афанасьев Дмитрий, группа к3340.

Цель работы: написать клиент и сервер на Python и разобраться, как они обмениваются данными через UDP и TCP.


Примеры ниже показывают ввод и ожидаемый результат. Это иллюстрации к коду, а не журнал выполненных запусков.

## 1. Обмен сообщениями по UDP

Сервер находится в файле task_1/server.py, клиент в task_1/client.py. Сервер создаёт сокет SOCK_DGRAM и ждёт сообщения на порту 8080. Клиент отправляет ему строку «Hello, server» с помощью sendto().

Через recvfrom() сервер получает текст и адрес клиента. Он выводит сообщение в терминал и отправляет ответ «Hello, client» на полученный адрес. Клиент принимает ответ и тоже выводит его. Соединение перед обменом устанавливать не нужно: UDP передаёт отдельные сообщения.

### task_1/server.py

```python
import socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("0.0.0.0", 8080))

while True:
    data, adres = server.recvfrom(1024)
    print(data.decode())
    response = "Hello, client".encode()
    server.sendto(response, adres)
```

### task_1/client.py

```python
import socket


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto("Hello, server".encode(),("127.0.0.1", 8080))
data, addr = client.recvfrom(1024)
print(data.decode())
client.close()
```

### Пример работы

```text
Терминал сервера:
Hello, server

Терминал клиента:
Hello, client
```

## 2. Площадь трапеции через TCP

В файле task_2/client.py пользователь вводит два основания трапеции и высоту. Клиент подключается к серверу на порту 9999 и отправляет эти числа. Сервер из файла task_2/server.py вычисляет площадь по формуле h * (a + b) / 2 и возвращает результат. Например, при a = 10, b = 10 и h = 10 площадь равна 100.

Здесь используется сокет SOCK_STREAM. TCP передаёт поток байтов, поэтому конец сообщения обозначен символом перевода строки \n. Метод makefile() позволяет читать данные из сокета как из файла, а readline() получает строку целиком.

### task_2/server.py

```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 9999))
server.listen(5)

while True:
    client, addr = server.accept()
    with client, client.makefile('r', encoding='utf-8') as request:
        try:
            a, b, h = map(float, request.readline().split())
            result = str(h * (a + b) / 2)
        except ValueError:
            result = "Ошибка: введите три числа"
        client.sendall((result + '\n').encode())
```

### task_2/client.py

```python
import socket

a = input("Первое основание: ")
b = input("Второе основание: ")
h = input("Высота: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 9999))
client.sendall(f'{a} {b} {h}\n'.encode())
with client.makefile('r', encoding='utf-8') as response:
    print(response.readline().strip())
client.close()
```

### Пример работы

```text
Первое основание: 10
Второе основание: 10
Высота: 10
100.0
```

## 3. HTML-страница

Сервер task_3/server.py принимает запросы на порту 8080. Он читает страницу из файла task_3/index.html и отправляет её вместе с HTTP-заголовками. В Content-Type указаны тип страницы и кодировка UTF-8. В Content-Length записана длина страницы в байтах.

Чтобы посмотреть страницу, нужно запустить сервер и открыть в браузере http://127.0.0.1:8080.

### task_3/server.py

```python
import socket
from pathlib import Path

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen(5)
print("Откройте http://127.0.0.1:8080")

while True:
    client, addr = server.accept()
    with client, client.makefile('rb') as request:
        # Читаем заголовки до пустой строки.
        line = request.readline()
        if not line:
            continue
        while line not in (b'\r\n', b''):
            line = request.readline()

        html = Path(__file__).with_name('index.html').read_bytes()
        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(html)}\r\n"
            "Connection: close\r\n\r\n"
        )
        client.sendall(headers.encode() + html)
```

### task_3/index.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Простой сервер на Python</title>
</head>
<body>
    <h1>Привет! Это простая HTML-страница.</h1>
    <p>Этот сервер написан на Python и работает через сокеты.</p>
    <p>Страница загружается из файла index.html.</p>
</body>
</html>
```

### Пример работы

```text
Терминал сервера:
Откройте http://127.0.0.1:8080

В браузере:
Привет! Это простая HTML-страница.
Этот сервер написан на Python и работает через сокеты.
Страница загружается из файла index.html.
```

## 4. Чат

В файле task_4/server.py подключения участников хранятся в списке CHAT. Для каждого клиента запускается отдельный поток с функцией chat(). Первой строкой клиент отправляет имя. Оно сохраняется в переменной name внутри его потока.

Новое подключение добавляется в список через CHAT.append(client). Когда приходит сообщение, сервер проходит по списку и отправляет его всем, кроме автора. Перед текстом он ставит имя отправителя. Для обхода используется CHAT.copy(), поскольку во время рассылки другой участник может выйти. LOCK не даёт нескольким потокам выполнять рассылку одновременно.

В клиенте task_4/client.py основной поток читает текст с клавиатуры, а второй получает сообщения от сервера. Благодаря этому пользователь может получать сообщения, пока набирает ответ. Для нескольких участников достаточно запустить один и тот же клиент в разных терминалах.

Команда /exit завершает подключение. При выходе сервер удаляет клиента из списка через CHAT.remove(client).

### task_4/server.py

```python
import socket
import threading

CHAT = []
LOCK = threading.Lock()


def chat(client):
    try:
        with client.makefile('r', encoding='utf-8') as messages:
            name = messages.readline().strip()
            if not name:
                return
            CHAT.append(client)
            for text in messages:
                if text.strip() == '/exit':
                    break
                with LOCK:
                    for user in CHAT.copy():
                        if user != client:
                            try:
                                user.sendall(f'{name}: {text}'.encode())
                            except OSError:
                                pass
    except OSError:
        pass
    finally:
        if client in CHAT:
            CHAT.remove(client)
        client.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 9999))
server.listen(5)
print("Чат запущен")

while True:
    client, addr = server.accept()
    threading.Thread(target=chat, args=(client,), daemon=True).start()
```

### task_4/client.py

```python
import socket
import threading


def receive_messages():
    try:
        with client.makefile('r', encoding='utf-8') as messages:
            for message in messages:
                print(message.strip())
    except OSError:
        pass
    print("Соединение закрыто. Для выхода введите /exit.")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 9999))
name = input("Ваше имя: ")
client.sendall((name + '\n').encode())
threading.Thread(target=receive_messages, daemon=True).start()

try:
    while True:
        message = input()
        client.sendall((message + '\n').encode())
        if message == '/exit':
            break
except (OSError, EOFError, KeyboardInterrupt):
    pass
finally:
    client.close()
```

### Пример работы

```text
Первый клиент:
Ваше имя: Анна
Привет

Второй клиент (подключён до отправки сообщения):
Ваше имя: Борис
Анна: Привет

Для выхода ввести /exit.
```

## 5. Журнал оценок

Сервер task_5/server.py работает на порту 8080. На запрос GET он возвращает страницу с формой и таблицей оценок. Через форму пользователь вводит предмет и оценку, после чего браузер отправляет POST.

Сервер читает тело запроса по длине из Content-Length. Функция parse_qs() разбирает поля формы. Для хранения используется словарь GRADES: название предмета служит ключом, а оценки хранятся в списке. Если предмета ещё нет, условие if создаёт пустой список. Затем append() добавляет в него оценку.

В таблице каждому предмету соответствует одна строка со всеми его оценками. Словарь сохраняется в grades.json и загружается при следующем запуске сервера.

После POST сервер перенаправляет браузер на GET. Поэтому при обновлении страницы оценка не отправляется повторно. Открыть журнал можно по адресу http://127.0.0.1:8080.

### task_5/server.py

```python
import socket
import json
from pathlib import Path
from urllib.parse import parse_qs
from html import escape

file = Path(__file__).with_name('grades.json')
GRADES = {}
if file.exists():
    GRADES = json.loads(file.read_text(encoding='utf-8'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen(5)
print("Откройте http://127.0.0.1:8080")

while True:
    client, addr = server.accept()
    with client, client.makefile('rb') as request:
        # Первая строка запроса, например: GET / HTTP/1.1.
        first_line = request.readline().decode().split()
        if not first_line:
            continue
        method, path, version = first_line

        headers = {}
        while True:
            line = request.readline()
            if line in (b'\r\n', b''):
                break
            key, value = line.decode().split(':', 1)
            headers[key.lower()] = value.strip()

        if method == 'POST':
            length = int(headers['content-length'])
            data = parse_qs(request.read(length).decode())
            subject = data['subject'][0]
            grade = data['grade'][0]
            if subject not in GRADES:
                GRADES[subject] = []
            GRADES[subject].append(grade)
            file.write_text(json.dumps(GRADES, ensure_ascii=False, indent=4), encoding='utf-8')
            # Перенаправление: обновление страницы не отправит оценку ещё раз.
            client.sendall(b'HTTP/1.1 303 See Other\r\nLocation: /\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
            continue

        rows = ''
        for subject, marks in GRADES.items():
            rows += f'<tr><td>{escape(subject)}</td><td>{escape(", ".join(map(str, marks)))}</td></tr>'

        html = f'''<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Оценки</title></head>
<body>
    <h1>Журнал оценок</h1>
    <form method="post" action="/">
        Дисциплина: <input name="subject" required>
        Оценка: <input name="grade" type="number" min="2" max="5" required>
        <button>Добавить</button>
    </form>
    <table border="1">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
</body>
</html>'''.encode()
        response = (
            'HTTP/1.1 200 OK\r\n'
            'Content-Type: text/html; charset=utf-8\r\n'
            f'Content-Length: {len(html)}\r\n'
            'Connection: close\r\n\r\n'
        )
        client.sendall(response.encode() + html)
```

### Пример работы

```text
Терминал сервера:
Откройте http://127.0.0.1:8080

В форме дважды добавить предмет Математика, сначала с оценкой 5, затем 4.
В таблице будет одна строка:
Математика | 5, 4
```

## Запуск

Сначала нужно запустить сервер, затем клиент. В заданиях 3 и 5 клиентом служит браузер. Перед переходом к следующему заданию сервер следует остановить: задания 2 и 4 используют порт 9999, а задания 3 и 5 используют порт 8080.

Программы рассчитаны на корректные запросы и ввод. Расширенная обработка ошибок в них не предусмотрена.




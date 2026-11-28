# Отчёт по лабораторной работе №1

Тема: Работа с сокетами

Студент: Моломожнов Никита Владимирович

---

## Содержание

1. [Цель работы](#1-цель-работы)
2. [Часть 1. Обмен сообщениями по UDP](#2-часть-1-обмен-сообщениями-по-udp)
3. [Часть 2. Вычисления через TCP](#3-часть-2-вычисления-через-tcp)
4. [Часть 3. Раздача HTML-страницы по HTTP](#4-часть-3-раздача-html-страницы-по-http)
5. [Часть 4. Многопользовательский чат](#5-часть-4-многопользовательский-чат)
6. [Часть 5. Веб-сервер (GET/POST)](#6-часть-5-веб-сервер-getpost)
7. [Вывод](#7-вывод)

---

## 1. Цель работы

Понять принципы межсокетного взаимодействия в вебе.
Научиться реализовывать базовую архитектуру клиент-сервер.

**Задачи:**
- Освоить работу с UDP и TCP сокетами.
- Реализовать HTTP-сервер с нуля.
- Освоить многопоточность для обслуживания нескольких клиентов.
- Реализовать обработку GET и POST запросов.

---

## 2. Часть 1. Обмен сообщениями по UDP

### 2.1. Цель

Реализовать клиент-серверное приложение на UDP.
Клиент отправляет «Hello, server», сервер отвечает «Hello, client».

### 2.2. Теоретическая часть

**UDP** — протокол без установления соединения. Быстрее TCP,
но не гарантирует доставку и порядок пакетов.

**В Python:**
- `socket.SOCK_DGRAM` — UDP-сокет.
- `sendto()` — отправить данные.
- `recvfrom()` — принять данные и адрес отправителя.

### 2.3. Реализация

**Сервер:**
```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("127.0.0.1", 5010))
print("сервер запущен")

data, client_address = server.recvfrom(1024)
print(f"Получено от {client_address}: {data.decode('utf-8')}")
response = "Hello, client"
server.sendto(response.encode('utf-8'), client_address)
print("Ответ отправлен клиенту")
server.close()
```

**Клиент:**
```python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = "Hello, server"
client.sendto(message.encode('utf-8'), ('127.0.0.1', 5010))
print(f"Отправлено: {message}")
response, server_address = client.recvfrom(1024)
print(f"Получен ответ: {response.decode('utf-8')}")
client.close()
```

### 2.4. Результат

**Сервер:**
```
сервер запущен
Получено от ('127.0.0.1', 54321): Hello, server
Ответ отправлен клиенту
```

**Клиент:**
```
Отправлено: Hello, server
Получен ответ: Hello, client
```

### 2.5. Вывод

Реализован UDP-обмен. Использованы `sendto()` и `recvfrom()`.

---

## 3. Часть 2. Вычисления через TCP

### 3.1. Цель

Реализовать TCP-приложение. Клиент вводит параметры трапеции,
сервер вычисляет площадь.

### 3.2. Теоретическая часть

**TCP** — протокол с установлением соединения. Гарантирует
доставку и порядок байт.

**Формула площади трапеции:**
```
S = (a + b) / 2 * h
```

### 3.3. Реализация

**Сервер:**
```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5011))
server.listen(1)
client_socket, client_address = server.accept()
data = client_socket.recv(1024).decode('utf-8')
a, b, h = map(float, data.split(','))
area = (a + b) / 2 * h
print(f"Площадь трапеции: {area}")
response = f"Площадь трапеции: {area}"
client_socket.send(response.encode('utf-8'))
client_socket.close()
server.close()
```

**Клиент:**
```python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5011))
print("Введите параметры трапеции:")
a = input("a: ")
b = input("b: ")
h = input("h: ")
message = f"{a},{b},{h}"
client.send(message.encode('utf-8'))
print(f"Отправлено: {message}")
response = client.recv(1024).decode('utf-8')
print(f"Ответ от сервера: {response}")
client.close()
```

### 3.4. Результат

**Ввод:** a=5, b=7, h=4

**Проверка:** S = (5 + 7) / 2 * 4 = 6 * 4 = 24

**Клиент:**
```
Отправлено: 5,7,4
Ответ от сервера: Площадь трапеции: 24.0
```

### 3.5. Вывод

Реализован TCP-обмен. Клиент передаёт параметры,
сервер вычисляет площадь.

---

## 4. Часть 3. Раздача HTML-страницы по HTTP

### 4.1. Цель

Реализовать HTTP-сервер, отдающий HTML-страницу из файла `index.html`.

### 4.2. Теоретическая часть

**HTTP-ответ** состоит из:
1. Строка статуса (`HTTP/1.1 200 OK`).
2. Заголовки (`Content-Type`, `Content-Length`).
3. Пустая строка.
4. Тело (HTML).

### 4.3. Реализация

**`index.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Лаба 1</title>
</head>
<body>
    <h1>Веб-программирование</h1>
    <p>Лабораторная работа №1</p>
    <p>Студент: Моломожнов Никита</p>
</body>
</html>
```

**Сервер:**
```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5012))
server.listen(1)
print("http://127.0.0.1:5012")

while True:
    client_socket, client_address = server.accept()
    request = client_socket.recv(1024).decode('utf-8')
    print("запрос клиента")
    print(request)
    print("конец запроса")

    try:
        with open('index.html', 'rb') as f:
            body = f.read()

        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        client_socket.send(headers.encode('utf-8') + body)
        print(f"Отправлено {len(body)} байт HTML")

    except FileNotFoundError:
        error_body = b"<h1>404 Not Found</h1>"
        headers = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(error_body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        client_socket.send(headers.encode('utf-8') + error_body)
        print("index.html не найден")

    client_socket.close()
```

Открыть в браузере: `http://127.0.0.1:5012`

### 4.4. Результат

Браузер отображает HTML-страницу. В терминале виден запрос:
```
GET / HTTP/1.1
Host: 127.0.0.1:5012
User-Agent: Mozilla/5.0 ...
```

### 4.5. Вывод

Реализован HTTP-сервер, отдающий HTML-файл.
Использованы заголовки `Content-Type` и `Content-Length`.

---

## 5. Часть 4. Многопользовательский чат

### 5.1. Цель

Реализовать многопользовательский чат на TCP с использованием `threading`.

### 5.2. Теоретическая часть

**Многопоточность** позволяет серверу обслуживать несколько
клиентов одновременно.

**Структура:**
- `clients` — список подключений.
- `lock` — защита от race condition.
- `broadcast` — рассылка всем, кроме отправителя.

### 5.3. Реализация

**Сервер:**
```python
import socket
import threading

clients = []
lock = threading.Lock()

def broadcast(msg, sender=None):
    with lock:
        for client in clients:
            if client != sender:
                try:
                    client.send(msg.encode('utf-8', errors='ignore'))
                except:
                    pass

def handle(sock):
    sock.send("Введите имя: ".encode())
    name = sock.recv(1024).decode('utf-8', errors='ignore').strip()
    with lock:
        clients.append(sock)
    broadcast(f" {name} в чате \n", sock)
    print(f"{name} подключился")

    while True:
        data = sock.recv(1024)
        if not data:
            break
        msg = data.decode('utf-8', errors='ignore').strip()
        if msg == '/quit':
            break
        broadcast(f"[{name}]: {msg}\n", sock)

    with lock:
        clients.remove(sock)
    broadcast(f" {name} вышел \n")
    print(f"{name} отключился")
    sock.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 5013))
server.listen(10)
print("Сервер запущен")

while True:
    sock, _ = server.accept()
    threading.Thread(target=handle, args=(sock,), daemon=True).start()
```

**Клиент:**
```python
import socket
import threading

def receive(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode('utf-8', errors='replace'), end='')
        except:
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5013))
threading.Thread(target=receive, args=(client,), daemon=True).start()

while True:
    try:
        msg = input()
        if not msg.strip():
            continue
        client.send(msg.encode('utf-8', errors='ignore'))
        if msg.strip() == '/quit':
            break
    except (KeyboardInterrupt, EOFError):
        print("\n[СИСТЕМА] Выход...")
        break

client.close()
```

### 5.4. Результат

**Никита пишет:** `Привет, Ваня!`

**Ваня видит:** `[Никита]: Привет, Ваня!`

**Ваня пишет:** `/quit`

**Никита видит:** ` Ваня вышел `

### 5.5. Вывод

Реализован многопользовательский чат. Сервер обслуживает
несколько клиентов через потоки. Есть идентификация по имени
и команда выхода `/quit`.

---

## 6. Часть 5. Веб-сервер (GET/POST)

### 6.1. Цель

Написать веб-сервер для обработки GET и POST запросов.
Сервер принимает дисциплину и оценку, хранит журнал
с группировкой по предмету.

### 6.2. Теоретическая часть

**GET** — получить данные.
**POST** — отправить данные (есть тело).

**Структура данных:**
```python
{
    "Математика": [5, 4, 5],
    "Физика": [3, 4]
}
```

**Почему словарь:**
- Ключ — дисциплина (уникальный).
- Значение — список оценок.
- Легко группировать.

### 6.3. Реализация

**Сервер:**
```python
import socket
import json
import os
from urllib.parse import unquote_plus

DATA_FILE = 'grades.json'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 5014))
server.listen(5)
print("Сервер запущен: http://127.0.0.1:5014")

while True:
    client, _ = server.accept()

    rfile = client.makefile('rb')
    request_line = rfile.readline().decode('iso-8859-1').rstrip('\r\n')
    parts = request_line.split(' ')
    method = parts[0]
    headers = {}
    while True:
        line = rfile.readline().decode('iso-8859-1').rstrip('\r\n')
        if line == '':
            break
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()

    body = ""
    if 'content-length' in headers:
        size = int(headers['content-length'])
        body = rfile.read(size).decode('utf-8')

    rfile.close()

    grades = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                grades = json.load(f)
        except:
            grades = {}

    if method == 'POST':
        form = {}
        for pair in body.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                form[unquote_plus(k)] = unquote_plus(v)

        subject = form.get('subject', '').strip()
        grade = form.get('grade', '').strip()

        if subject and grade.isdigit():
            if subject in grades:
                grades[subject].append(int(grade))
            else:
                grades[subject] = [int(grade)]

            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(grades, f, ensure_ascii=False, indent=2)

    rows = ""
    for subject in grades:
        marks = grades[subject]
        marks_str = ""
        for m in marks:
            marks_str += str(m) + " "
        rows += "<tr><td>" + subject + "</td><td>" + marks_str + "</td></tr>"

    if rows == "":
        rows = "<tr><td colspan='2'>Журнал пуст</td></tr>"

    html = "<!DOCTYPE html>"
    html += "<html><head><meta charset='UTF-8'><title>Журнал</title></head>"
    html += "<body>"
    html += "<h1>Журнал</h1>"
    html += "<form method='POST'>"
    html += "<input name='subject' placeholder='Дисциплина' required>"
    html += "<input name='grade' type='number' min='1' max='5' required>"
    html += "<button>Добавить</button>"
    html += "</form>"
    html += "<table border='1' cellpadding='8'>"
    html += "<tr><th>Дисциплина</th><th>Оценки</th></tr>"
    html += rows
    html += "</table>"
    html += "</body></html>"

    body_bytes = html.encode('utf-8')
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Type: text/html; charset=utf-8\r\n"
    response += "Content-Length: " + str(len(body_bytes)) + "\r\n"
    response += "Connection: close\r\n"
    response += "\r\n"

    client.sendall(response.encode('utf-8') + body_bytes)
    client.close()
```

Открыть в браузере: `http://127.0.0.1:5014`

### 6.4. Результат

**Добавлены оценки:**

| Дисциплина | Оценки |
| :--- | :--- |
| Математика | 5 4 5 |
| Русский | 4 |
| Физика | 3 |

**Файл `grades.json`:**
```json
{
  "Математика": [5, 4, 5],
  "Русский": [4],
  "Физика": [3]
}
```

### 6.5. Вывод

Реализован веб-сервер с GET/POST. Данные хранятся
в словаре с группировкой по предмету и сохраняются в JSON.

---

## 7. Вывод

В ходе лабораторной работы были реализованы **5 частей**:

| Часть | Тема | Протокол | Технологии |
| :--- | :--- | :--- | :--- |
| 1 | Обмен сообщениями | UDP | `socket`, `SOCK_DGRAM` |
| 2 | Вычисления | TCP | `socket`, `SOCK_STREAM` |
| 3 | Раздача HTML | HTTP | `socket`, HTTP-заголовки |
| 4 | Чат | TCP | `socket`, `threading` |
| 5 | Веб-сервер GET/POST | HTTP | `socket`, `json`, `threading` |

**Полученные навыки:**
- Работа с UDP и TCP сокетами.
- Ручной разбор HTTP-протокола.
- Обработка GET и POST запросов.
- Многопоточность для обслуживания клиентов.
- Группировка данных через словарь.
- Сохранение данных в JSON.
- Генерация HTML-страниц.
- Работа с `rfile` и `Content-Length`.

**Все задачи выполнены.**
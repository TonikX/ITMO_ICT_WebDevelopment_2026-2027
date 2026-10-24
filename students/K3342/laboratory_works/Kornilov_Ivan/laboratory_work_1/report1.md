# Лабораторная работа 1. Работа с сокетами

**Студент:** Корнилов Иван  
**Группа:** K3342  
**Дисциплина:** Веб-программирование

## Цель работы

Понять принципы межсокетного взаимодействия и реализовать базовую клиент-серверную архитектуру на Python с библиотекой `socket`.

Все серверы слушают `localhost:8080` и обрабатывают запросы в цикле `while True`. Остановка — `Ctrl+C`. Сначала запускается сервер, потом клиент или браузер.

## Задание 1. Обмен сообщениями по UDP

UDP не устанавливает соединение: клиент сразу отправляет датаграмму через `sendto()`, сервер принимает её `recvfrom()` и отвечает на адрес отправителя.

**Файлы:** `task_1/server.py`, `task_1/client.py`

Клиент отправляет строку `Hello, server`. Сервер печатает её и отвечает `Hello, client`. Сервер не завершается после первого обмена и ждёт следующие датаграммы.

Фрагмент сервера:

```python
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("localhost", 8080))

while True:
    data, client_address = server_socket.recvfrom(1024)
    print(data.decode("utf-8"))
    server_socket.sendto("Hello, client".encode("utf-8"), client_address)
```

Клиент читает ответ через `recv()` и печатает его.

**Запуск:** в одном терминале `python3 task_1/server.py`, в другом `python3 task_1/client.py`.

**Ожидаемый результат:** сервер печатает `Hello, server`, клиент печатает `Hello, client`.

## Задание 2. Вычисления через TCP

TCP сначала устанавливает соединение: клиент вызывает `connect()`, сервер — `accept()`. Доставка и порядок байт гарантированы, поэтому через такой канал удобно передавать параметры вычисления.

**Вариант 1 — теорема Пифагора.** Клиент вводит два катета с клавиатуры, сервер считает гипотенузу `c = sqrt(a² + b²)` и закрывает соединение. Затем сервер снова вызывает `accept()` и ждёт следующего клиента.

**Файлы:** `task_2/server.py`, `task_2/client.py`

Фрагмент сервера:

```python
while True:
    client_connection, _ = server_socket.accept()
    request = client_connection.recv(1024).decode("utf-8")
    a, b = map(float, request.split())
    hypotenuse = math.sqrt(a ** 2 + b ** 2)
    client_connection.sendall(f"Гипотенуза: {hypotenuse:.4f}".encode("utf-8"))
    client_connection.close()
```

**Запуск:** `python3 task_2/server.py`, затем `python3 task_2/client.py`. Пример ввода: `3 4`. Ответ: `Гипотенуза: 5.0000`.

## Задание 3. Раздача HTML-страницы по HTTP

HTTP-ответ — текст: строка статуса, заголовки, пустая строка, тело. Сервер читает `index.html` рядом со скриптом через `Path(__file__).with_name("index.html")`, считает длину тела для `Content-Length` и отправляет готовый ответ каждому подключившемуся клиенту. Клиентского скрипта нет: страница открывается в браузере.

**Файлы:** `task_3/server.py`, `task_3/index.html`

Фрагмент сервера:

```python
html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
body_bytes = html.encode("utf-8")
headers = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=UTF-8\r\n"
    f"Content-Length: {len(body_bytes)}\r\n"
    "Connection: close\r\n"
    "\r\n"
)
response = headers.encode("utf-8") + body_bytes

while True:
    client_connection, _ = server_socket.accept()
    client_connection.recv(1024)
    client_connection.sendall(response)
    client_connection.close()
```

**Запуск:** `python3 task_3/server.py`, затем открыть http://localhost:8080/ в браузере.

## Задание 4. Многопользовательский чат

Чат работает по TCP. Один клиентский скрипт запускается несколькими пользователями в разных терминалах. Сервер хранит словарь `сокет → имя` и для каждого подключения создаёт поток `threading.Thread`. Входящие сообщения рассылаются всем, кроме отправителя.

Идентификация: клиент спрашивает имя (`Имя: `) и отправляет его первым сообщением. На клиенте отдельный поток читает сообщения из сокета, основной поток читает ввод с клавиатуры. Выход: команда `/exit`. При входе и выходе сервер рассылает служебные сообщения.

**Файлы:** `task_4/server.py`, `task_4/client.py`

Фрагмент сервера:

```python
clients = {}

while True:
    client_socket, _ = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
```

**Запуск:** `python3 task_4/server.py`, затем в двух или трёх терминалах `python3 task_4/client.py`.

## Задание 5. Простой веб-сервер GET/POST

Сервер разбирает HTTP вручную: читает заголовки до пустой строки `\r\n\r\n`, из первой строки берёт метод и путь, для POST дочитывает тело по `Content-Length`. Поля формы разбираются через `parse_qs`. Оценки хранятся в `defaultdict(list)`: ключ — дисциплина, значение — список оценок. Если по математике пришло две оценки, в журнале одна запись со списком из двух чисел.

| Метод | Путь | Действие |
| --- | --- | --- |
| GET | `/` | Показать журнал и форму |
| POST | `/` | Сохранить оценку и показать журнал |

**Файл:** `task_5/server.py`

Фрагмент обработки запроса:

```python
method, path, body = read_request(connection)
if method == "POST":
    form = parse_qs(body)
    subject = form.get("subject", [""])[0]
    grade = form.get("grade", [""])[0]
    if subject and grade:
        grades[subject].append(grade)
send_response(connection, render_page())
```

**Запуск:** `python3 task_5/server.py`, затем открыть http://localhost:8080/ и добавить несколько оценок. После `Математика / 5` и `Математика / 4` страница показывает `Математика: 5, 4`. Данные живут в памяти процесса и сбрасываются при перезапуске.

## Вывод

Реализованы пять программ на сокетах: обмен по UDP, вычисление по TCP, раздача HTML, многопользовательский чат с потоками и HTTP-сервер с журналом оценок.

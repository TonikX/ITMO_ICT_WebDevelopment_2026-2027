# Лабораторная работа № 1. Работа с сокетами

**Студент:** Илхом Солиев  
**Группа:** К3339

## Цель работы

Реализовать обмен данными между клиентом и сервером с помощью сокетов и изучить протоколы UDP, TCP и HTTP.

## Задание 1. Обмен по UDP

UDP позволяет отправлять датаграммы без установки соединения. Клиент отправляет сообщение, сервер получает его и отвечает отправителю.

```python
# Клиент
client.sendto(b"Hello, server", ("127.0.0.1", 9090))
message, address = client.recvfrom(1024)

# Сервер
message, address = server.recvfrom(1024)
print(message.decode())
server.sendto(b"Hello, client", address)
```

## Задание 2. Вычисление по TCP

Клиент передаёт серверу основание и высоту. Сервер вычисляет их произведение `S = a × h` и отправляет результат обратно.

```python
# Клиент отправляет параметры и получает ответ
client.sendall(f"{base} {height}".encode())
print(client.recv(1024).decode())

# Сервер вычисляет результат
base, height = map(float, connection.recv(1024).decode().split())
area = base * height
connection.sendall(str(area).encode())
```

## Задание 3. Раздача HTML по HTTP

Сервер читает `index.html` и формирует HTTP-ответ. `Content-Length` задаёт размер HTML-тела в байтах.

```python
body = Path(__file__).with_name("index.html").read_bytes()
response = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/html; charset=utf-8\r\n"
    + f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    + body
)
connection.sendall(response)
```

## Задание 4. Многопользовательский чат

Сервер запускает отдельный поток для каждого подключения. Имя клиента сохраняется вместе с его сокетом, а сообщения пересылаются всем остальным участникам. Команда `/quit` завершает работу клиента в чате.

```python
# Обработка каждого клиента в отдельном потоке
threading.Thread(
    target=handle_client,
    args=(connection,),
    daemon=True
).start()

# Рассылка сообщения с именем отправителя
sender_name = next(name for name, connection in clients if connection == sender)
for _, connection in clients:
    if connection != sender:
        connection.sendall(f"{sender_name}: {message}\n".encode("utf-8"))
```

## Задание 5. HTTP-сервер оценок

Сервер принимает данные формы методом `POST` и сохраняет список оценок для каждого предмета в `grades.json`. При запросе страницы оценки отображаются в HTML-таблице.

```python
# Добавление оценки в список предмета
grades.setdefault(subject, []).append(grade)
file.write_text(json.dumps(grades, ensure_ascii=False, indent=2), encoding="utf-8")

# Сохранение данных POST и подготовка HTML-страницы
if method == "POST":
    form = parse_qs(body.decode())
    save_grade(form["subject"][0], form["grade"][0])

response_body = page().encode("utf-8")
response = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/html; charset=utf-8\r\n"
    + f"Content-Length: {len(response_body)}\r\n\r\n".encode()
    + response_body
)
connection.sendall(response)
```

## Вывод

В работе реализованы обмен сообщениями по UDP и TCP, многопользовательский чат и HTTP-серверы. На практике использованы сокеты для передачи данных и разобрана структура HTTP-запроса и ответа.

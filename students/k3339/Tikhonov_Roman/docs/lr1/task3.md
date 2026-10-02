# Задание 3. Раздача HTML-страницы по HTTP

## Протокол

**HTTP** (HyperText Transfer Protocol) — прикладной протокол поверх TCP. HTTP-ответ
состоит из стартовой строки (статус), заголовков, пустой строки и тела. В этом задании
сервер вручную собирает такой ответ и отдаёт содержимое файла `index.html`.

| Параметр | Значение                        |
|----------|---------------------------------|
| Протокол | HTTP поверх TCP (`SOCK_STREAM`) |
| Адрес    | `127.0.0.1`                     |
| Порт     | `8083`                          |

## Эндпоинты

| Метод | URL | Описание                                    |
|-------|-----|---------------------------------------------|
| `GET` | `/` | Вернуть HTML-страницу из файла `index.html` |

## Код сервера

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 8083))
sock.listen(1)

conn, addr = sock.accept()
print("Подключился клиент:", addr)

data = conn.recv(1024)
print(data.decode())

f = open("index.html", encoding="utf-8")
body = f.read()
f.close()
body_bytes = body.encode("utf-8")

response = "HTTP/1.1 200 OK\r\n"
response += "Content-Type: text/html; charset=utf-8\r\n"
response += "Content-Length: " + str(len(body_bytes)) + "\r\n"
response += "\r\n"
response += body

conn.send(response.encode("utf-8"))
conn.close()
sock.close()
```

## Файл index.html

```html

<html>
<head>
    <title>Моя страница</title>
</head>
<body>
<h1>Привет, сервер работает!</h1>
<p>Это страница, которую сервер загружает из файла index.html и отправляет клиенту по HTTP.</p>
</body>
</html>
```

## Пример работы в терминале

**Окно 1 — сервер (из папки src/task3):**

```
> python server.py
Сервер запущен. Откройте: http://127.0.0.1:8083
Подключился клиент: ('127.0.0.1', 51234)
GET / HTTP/1.1
Host: 127.0.0.1:8083
```

**Браузер** открывает `http://127.0.0.1:8083` и отображает страницу «Привет, сервер работает!».

## Запуск

1. Терминал 1 (из папки `src/task3`): `python server.py`
2. Открыть в браузере `http://127.0.0.1:8083`
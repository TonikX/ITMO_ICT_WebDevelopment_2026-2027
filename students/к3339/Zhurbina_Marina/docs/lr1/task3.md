# Задание 3. Раздача HTML-страницы по HTTP

## Протокол
**HTTP** (HyperText Transfer Protocol) — прикладной протокол поверх TCP. HTTP-ответ
содержит стартовую строку, заголовки, пустую строку и тело. Сервер вручную собирает
ответ и отдаёт содержимое файла `index.html`.

| Параметр | Значение |
|----------|----------|
| Протокол | HTTP поверх TCP (`SOCK_STREAM`) |
| Адрес | `127.0.0.1` |
| Порт | `9003` |

## Эндпоинты
| Метод | URL | Описание |
|-------|-----|----------|
| `GET` | `/` | Вернуть HTML-страницу из файла `index.html` |

## Код сервера
```python
import socket

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(("127.0.0.1", 9003))
listener.listen(1)

conn, addr = listener.accept()
print("Клиент:", addr)
conn.recv(1024)

with open("index.html", encoding="utf-8") as f:
    html = f.read()
html_bytes = html.encode("utf-8")

answer = "HTTP/1.1 200 OK\r\n"
answer += "Content-Type: text/html; charset=utf-8\r\n"
answer += "Content-Length: " + str(len(html_bytes)) + "\r\n"
answer += "\r\n"
answer += html

conn.send(answer.encode("utf-8"))
conn.close()
listener.close()
```

## Файл index.html
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Мой сайт</title>
</head>
<body>
    <h1>Добро пожаловать!</h1>
    <p>Эта страница была прочитана сервером из файла и отправлена по HTTP.</p>
</body>
</html>
```

## Пример работы в терминале
**Окно 1 — сервер (из папки src/task3):**
```
> python server.py
Сервер активен. Откройте: http://127.0.0.1:9003
Клиент: ('127.0.0.1', 53333)
```
**Браузер** открывает `http://127.0.0.1:9003` и отображает страницу «Добро пожаловать!».

## Запуск
1. Терминал 1 (из папки `src/task3`): `python server.py`
2. Открыть в браузере `http://127.0.0.1:9003`
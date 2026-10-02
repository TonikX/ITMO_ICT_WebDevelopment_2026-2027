# Задание 1. Обмен сообщениями по UDP

## Протокол

**UDP** (User Datagram Protocol) — протокол без установления соединения. Отправитель
просто посылает датаграмму, не дожидаясь подтверждения. Это быстро, но не гарантирует
доставку и порядок пакетов. В Python для UDP используется тип сокета `SOCK_DGRAM`
и методы `sendto()` / `recvfrom()`.

| Параметр | Значение                 |
|----------|--------------------------|
| Протокол | UDP (`SOCK_DGRAM`)       |
| Адрес    | `127.0.0.1`              |
| Порт     | `8081`                   |
| Методы   | `sendto()`, `recvfrom()` |

## Код сервера

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 8081))

data, addr = sock.recvfrom(1024)
print(data.decode())

sock.sendto(b"Hello, client", addr)
sock.close()
```

## Код клиента

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Hello, server", ("127.0.0.1", 8081))

data, addr = sock.recvfrom(1024)
print(data.decode())
sock.close()
```

## Пример работы в терминале

**Окно 1 — сервер:**

```
> python src/task1/server.py
Hello, server
```

**Окно 2 — клиент:**

```
> python src/task1/client.py
Hello, client
```

## Запуск

1. Терминал 1: `python src/task1/server.py`
2. Терминал 2: `python src/task1/client.py`
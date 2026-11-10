# Задание 1. Обмен сообщениями по UDP

## Протокол
**UDP** (User Datagram Protocol) — протокол без установления соединения. Датаграмма
отправляется сразу, без подтверждения. В Python используется сокет `SOCK_DGRAM`
и методы `sendto()` / `recvfrom()`.

| Параметр | Значение |
|----------|----------|
| Протокол | UDP (`SOCK_DGRAM`) |
| Адрес | `127.0.0.1` |
| Порт | `9001` |
| Методы | `sendto()`, `recvfrom()` |

## Код сервера
```python
import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("127.0.0.1", 9001))

received, client_address = udp_socket.recvfrom(1024)
print("Принято:", received.decode())

udp_socket.sendto("Ответ сервера".encode(), client_address)
udp_socket.close()
```

## Код клиента
```python
import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.sendto("Запрос клиента".encode(), ("127.0.0.1", 9001))

received, _ = udp_socket.recvfrom(1024)
print("Получено:", received.decode())
udp_socket.close()
```


## Пример работы в терминале
**Окно 1 — сервер:**
```
> python src/task1/server.py
Принято: Запрос клиента
```
**Окно 2 — клиент:**
```
> python src/task1/client.py
Получено: Ответ сервера
```

## Запуск
1. Терминал 1: `python src/task1/server.py`
2. Терминал 2: `python src/task1/client.py`
# Задание 2. Решение квадратного уравнения по TCP

## Протокол
**TCP** (Transmission Control Protocol) — протокол с установлением соединения,
гарантирует доставку и порядок данных. Используется сокет `SOCK_STREAM`:
на сервере `bind`/`listen`/`accept`, на клиенте — `connect`.

| Параметр | Значение |
|----------|----------|
| Протокол | TCP (`SOCK_STREAM`) |
| Адрес | `127.0.0.1` |
| Порт | `9002` |
| Операция | Решение уравнения `ax² + bx + c = 0` |

## Постановка задачи
Клиент вводит коэффициенты `a`, `b`, `c` квадратного уравнения и передаёт их серверу.
Сервер находит корни через дискриминант `D = b² − 4ac` и возвращает ответ.

## Код сервера
```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 9002))
server.listen(1)

connection, _ = server.accept()
raw = connection.recv(1024).decode()
a, b, c = raw.split()
a = float(a)
b = float(b)
c = float(c)

d = b * b - 4 * a * c
if d > 0:
    x1 = (-b + d ** 0.5) / (2 * a)
    x2 = (-b - d ** 0.5) / (2 * a)
    result = f"Два корня: x1={x1:.2f}, x2={x2:.2f}"
elif d == 0:
    x1 = -b / (2 * a)
    result = f"Один корень: x={x1:.2f}"
else:
    result = "Действительных корней нет"

connection.send(result.encode())
connection.close()
server.close()
```

## Код клиента
```python
import socket

a = input("Введите a: ")
b = input("Введите b: ")
c = input("Введите c: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 9002))
client.send((a + " " + b + " " + c).encode())

answer = client.recv(1024).decode()
print("Ответ сервера:", answer)
client.close()
```

## Пример работы в терминале
**Окно 1 — сервер:**
```
> python src/task2/server.py
```
**Окно 2 — клиент:**
```
> python src/task2/client.py
Введите a: 1
Введите b: -5
Введите c: 6
Ответ сервера: Два корня: x1=3.00, x2=2.00
```

## Запуск
1. Терминал 1: `python src/task2/server.py`
2. Терминал 2: `python src/task2/client.py`
3. Ввести коэффициенты `a`, `b`, `c`.
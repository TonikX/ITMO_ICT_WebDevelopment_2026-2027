# Задание 2. Вычисления по TCP

## Протокол

**TCP** (Transmission Control Protocol) — протокол с установлением соединения.
Он гарантирует доставку и порядок байт, но требует предварительного соединения.
В Python для TCP используется тип сокета `SOCK_STREAM`: на сервере
`bind`/`listen`/`accept`, на клиенте — `connect`.

| Параметр | Значение                            |
|----------|-------------------------------------|
| Протокол | TCP (`SOCK_STREAM`)                 |
| Адрес    | `127.0.0.1`                         |
| Порт     | `8082`                              |
| Операция | Площадь параллелограмма `S = a · h` |

## Постановка задачи

Клиент вводит с клавиатуры основание `a` и высоту `h` параллелограмма, отправляет их
серверу. Сервер вычисляет площадь `S = a * h` и возвращает результат клиенту.

## Код сервера

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 8082))
sock.listen(1)

conn, addr = sock.accept()

data = conn.recv(1024).decode()
a, h = data.split()
a = float(a)
h = float(h)
s = a * h

conn.send(str(s).encode())
conn.close()
sock.close()
```

## Код клиента

```python
import socket

a = input("Введите основание a: ")
h = input("Введите высоту h: ")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 8082))

sock.send((a + " " + h).encode())

data = sock.recv(1024).decode()
print("Площадь параллелограмма: " + data)
sock.close()
```

## Пример работы в терминале

**Окно 1 — сервер:**

```
> python src/task2/server.py
```

**Окно 2 — клиент:**

```
> python src/task2/client.py
Введите основание a: 3
Введите высоту h: 4
Площадь параллелограмма: 12.0
```

## Запуск

1. Терминал 1: `python src/task2/server.py`
2. Терминал 2: `python src/task2/client.py`
3. Ввести основание и высоту.
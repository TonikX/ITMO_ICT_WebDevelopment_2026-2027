# Лабораторная работа 1. Работа с сокетами

## Цель работы

Понять принципы межсокетного взаимодействия в вебе и научиться реализовывать
базовую архитектуру клиент-сервер на языке Python с использованием
стандартной библиотеки `socket`.

## Используемые технологии

- **Python 3.13** — язык реализации
- **`socket`** — стандартная библиотека для работы с сокетами
- **`threading`** — многопоточность (задания 4 и 5)
- **`urllib.parse`**, **`html`** — разбор HTTP-запроса и экранирование

## Задание 1. Обмен сообщениями по UDP

### Краткое описание протокола

UDP (User Datagram Protocol) — протокол без установления соединения.
Отправитель формирует датаграмму и отправляет её в сеть, не дожидаясь
подтверждения от получателя. Это быстрее TCP, но не гарантирует ни доставку,
ни порядок пакетов.

### Код сервера

```python
import socket

HOST = '127.0.0.1'
PORT = 9090

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"[Сервер] Запущен на {HOST}:{PORT}, ждём сообщения...")

    while True:
        data, client_address = server_socket.recvfrom(1024)
        message = data.decode('utf-8')
        print(f"[Сервер] Получено от {client_address}: {message}")

        response = "Hello, client"
        server_socket.sendto(response.encode('utf-8'), client_address)
        print(f"[Сервер] Отправлено: {response}")

if __name__ == '__main__':
    main()
```

### Код клиента
```python
import socket

HOST = '127.0.0.1'
PORT = 9090

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = "Hello, server"
    client_socket.sendto(message.encode('utf-8'), (HOST, PORT))
    print(f"[Клиент] Отправлено: {message}")

    data, _ = client_socket.recvfrom(1024)
    response = data.decode('utf-8')
    print(f"[Клиент] Получено от сервера: {response}")

    client_socket.close()

if __name__ == '__main__':
    main()
```

### Пример работы
*Сервер*
```
[Сервер] Запущен на 127.0.0.1:9090, ждём сообщения...
[Сервер] Получено от ('127.0.0.1', 54321): Hello, server
[Сервер] Отправлено: Hello, client
```

*Клиент*
```
[Клиент] Отправлено: Hello, server
[Клиент] Получено от сервера: Hello, client
```

## Задание 2. Вычисления через TCP

### Краткое описание протокола
TCP (Transmission Control Protocol) — протокол с установлением соединения.
Перед обменом данными клиент и сервер обмениваются служебными пакетами
(three-way handshake), после чего TCP гарантирует доставку и порядок байт.

### Вариант
Номер варианта: 4 - Поиск площади параллелограмма

Формула: S = a · h, где a — основание, h — высота, опущенная на это
основание

### Код сервера
```python
import socket

HOST = '127.0.0.1'
PORT = 9091

def calculate_parallelogram_area(base: float, height: float) -> float:
    """Площадь параллелограмма: S = a * h"""
    return base * height

def handle_client(conn, addr):
    print(f"[Сервер] Подключён клиент {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                # Клиент закрыл соединение
                print(f"[Сервер] Клиент {addr} отключился")
                break

            message = data.decode('utf-8').strip()
            print(f"[Сервер] Получено от {addr}: {message}")

            # Ожидаем два числа через пробел
            try:
                parts = message.split()
                if len(parts) != 2:
                    raise ValueError("Нужно ровно два числа")
                base = float(parts[0])
                height = float(parts[1])
            except ValueError as e:
                error_msg = f"Ошибка: некорректный ввод ({e}). Пришлите два числа через пробел"
                conn.sendall(error_msg.encode('utf-8'))
                continue

            if base <= 0 or height <= 0:
                conn.sendall("Ошибка: стороны должны быть положительными.".encode('utf-8'))
                continue

            area = calculate_parallelogram_area(base, height)
            response = f"Площадь параллелограмма: {area}"
            conn.sendall(response.encode('utf-8'))
            print(f"[Сервер] Отправлено: {response}")
    finally:
        conn.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Позволяет переиспользовать порт сразу после закрытия сервера
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # очередь до 5 подключений
    print(f"[Сервер] Запущен на {HOST}:{PORT}, ждём подключений...")

    while True:
        conn, addr = server_socket.accept()
        handle_client(conn, addr)

if __name__ == '__main__':
    main()
```

### Код клиента
```python
import socket

HOST = '127.0.0.1'
PORT = 9091

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"[Клиент] Подключён к {HOST}:{PORT}")

    try:
        while True:
            base_str = input("Введите основание параллелограмма (или 'exit' для выхода): ").strip()
            if base_str.lower() == 'exit':
                break
            height_str = input("Введите высоту параллелограмма: ").strip()

            message = f"{base_str} {height_str}"
            client_socket.sendall(message.encode('utf-8'))

            data = client_socket.recv(1024)
            if not data:
                print("[Клиент] Сервер закрыл соединение")
                break
            print(f"[Клиент] Ответ сервера: {data.decode('utf-8')}")
    finally:
        client_socket.close()
        print("[Клиент] Соединение закрыто")

if __name__ == '__main__':
    main()
```

### Пример работы
*Сервер*
```
Введите основание (или 'exit'): 5
Введите высоту: 10
[Клиент] Ответ: Площадь параллелограмма: 50.0
Введите основание (или 'exit'): 2.5
Введите высоту: 4
[Клиент] Ответ: Площадь параллелограмма: 10.0
Введите основание (или 'exit'): exit
```

## Задание 3. Раздача HTML-страницы по HTTP

### Формат HTTP-ответа
HTTP-ответ — обычный текст, состоящий из трёх частей
- Строка статуса — HTTP/1.1 200 OK
- Заголовки — Content-Type, Content-Length, Connection
- Пустая строка (\r\n\r\n) — разделитель заголовков и тела
- Тело — собственно HTML

### Код
```python
import socket
import os

HOST = '127.0.0.1'
PORT = 9092

def build_http_response(
        body: bytes,
        content_type: str = 'text/html; charset=utf-8',
        status: str = '200 OK'
) -> bytes:
    """Собирает HTTP-ответ по стандартному формату."""
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return headers.encode('utf-8') + body

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[Сервер] Запущен на http://{HOST}:{PORT}")

    index_path = os.path.join(os.path.dirname(__file__), 'index.html')

    while True:
        conn, addr = server_socket.accept()
        print(f"[Сервер] Подключение от {addr}")
        try:
            # Читаем запрос
            request = conn.recv(4096).decode('utf-8', errors='ignore')
            first_line = request.split('\r\n')[0]
            print(f"[Сервер] Запрос: {first_line}")

            # Отдаём index.html на любой GET-запрос
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    body = f.read()
                response = build_http_response(body)
            else:
                body = b"<h2>index.html not Found</h2>"
                response = build_http_response(body, status='404 Not Found')

            conn.sendall(response)
        except Exception as e:
            print(f"[Сервер] Ошибка: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    main()
```

### Пример работы
```
[Сервер] Запущен на http://127.0.0.1:9092
[Сервер] Запрос: GET / HTTP/1.1
```

## Задание 4. Многопользовательский чат
### Архитектура
Сервер держит по одному потоку (threading.Thread) на каждого клиента
Для каждого соединения создаётся отдельный поток, который читает сообщения
от своего клиента и рассылает их всем остальным

Общий список клиентов (dict[socket, str]) защищён threading.Lock —
это исключает гонки данных при одновременном обращении из разных потоков

### Код сервера
```python
import socket
import threading

HOST = '127.0.0.1'
PORT = 9093

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f"[Сервер] Слушает {self.host}:{self.port}")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(
                target=self.handle_client,
                args=(conn, addr),
                daemon=True,
            ).start()

    def handle_client(self, conn, addr):
        name = None
        try:
            name = conn.recv(1024).decode('utf-8').strip()
            if not name:
                return
            with self.lock:
                self.clients[conn] = name
            self._broadcast(f"[СИСТЕМА] {name} присоединился", exclude=conn)

            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8').rstrip('\r\n')
                if message.lower() in ('!exit', '/exit'):
                    break
                self._broadcast(f"{name}: {message}", exclude=conn)
        finally:
            with self.lock:
                self.clients.pop(conn, None)
            if name:
                self._broadcast(f"[СИСТЕМА] {name} покинул чат")
            conn.close()

    def _broadcast(self, message, exclude=None):
        payload = (message + '\n').encode('utf-8')
        with self.lock:
            recipients = list(self.clients.keys())
        for client in recipients:
            if client is exclude:
                continue
            try:
                client.sendall(payload)
            except OSError:
                with self.lock:
                    self.clients.pop(client, None)

if __name__ == '__main__':
    ChatServer(HOST, PORT).start()
```

### Код клиента
```python
import socket
import threading

HOST = '127.0.0.1'
PORT = 9093
EXIT_COMMAND = '!exit'

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def start(self):
        self.socket.connect((self.host, self.port))
        name = input("Введите ваше имя: ").strip() or "Аноним"
        self._send(name)

        threading.Thread(target=self._receive_loop, daemon=True).start()
        self._send_loop()

    def _send_loop(self):
        try:
            while self.running:
                text = input()
                if text.strip().lower() == EXIT_COMMAND:
                    self._send(EXIT_COMMAND)
                    break
                self._send(text)
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            self._shutdown()

    def _send(self, text):
        try:
            self.socket.sendall((text + '\n').encode('utf-8'))
        except OSError:
            self.running = False

    def _receive_loop(self):
        while self.running:
            try:
                data = self.socket.recv(1024)
            except OSError:
                break
            if not data:
                break
            for line in data.decode('utf-8').splitlines():
                print(f"\r{line}\n> ", end='', flush=True)
        self.running = False

    def _shutdown(self):
        self.running = False
        try:
            self.socket.close()
        except OSError:
            pass

if __name__ == '__main__':
    ChatClient(HOST, PORT).start()
```

### Пример работы
Запускаются три терминала: сервер + два клиента

*Сервер*
```
[Сервер] Слушает 127.0.0.1:9093
[Сервер] Алиса подключилась
[Сервер] Боб подключился
```

*Клиент*
```
[СИСТЕМА] Боб присоединился
[СИСТЕМА] Алиса присоединился
> Привет!
[СИСТЕМА] Боб покинул чат
```

## Задание 5. Простой веб-сервер (GET/POST)

Оценки хранятся в словаре, сгруппированном по дисциплинам.
Ключ — название дисциплины, значение — список оценок. Такая структура
обеспечивает автоматическую группировку: все оценки по предмету лежат
в одном списке
![task_5_api_table.png](img/task_5_api_table.png)

```python
import socket
import threading
from html import escape
from urllib.parse import parse_qs

HOST = '127.0.0.1'
PORT = 9094

class GradesServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.grades: dict[str, list[int]] = {}
        self.lock = threading.Lock()

    # ... полный код в репозитории
```

### Пример работы!
![Снимок экрана 2026-09-28 175337.png](img%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-09-28%20175337.png)
![Снимок экрана 2026-09-28 175341.png](img%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-09-28%20175341.png)
![Снимок экрана 2026-09-28 175350.png](img%2F%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-09-28%20175350.png)
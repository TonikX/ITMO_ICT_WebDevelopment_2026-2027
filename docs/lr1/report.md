# Отчёт по лабораторной работе №1. Работа с сокетами

**Цель работы:** Понять принципы межсокетного взаимодействия в вебе. Научиться реализовывать базовую архитектуру клиент-сервер на протоколах транспортного и прикладного уровней.

---

## Задание 1. Обмен сообщениями по UDP

**Описание протокола:** UDP (User Datagram Protocol) — протокол транспортного уровня без установления соединения. Отправитель посылает датаграмму, не дожидаясь подтверждения от получателя. Это обеспечивает высокую скорость, но не гарантирует доставку и порядок пакетов. В Python используется `socket.SOCK_DGRAM`.

??? info "Полный листинг кода клиента и сервера"
    **udp_server.py**
    ```python
    import socket

    HOST = '127.0.0.1'
    PORT = 8081

    def run_udp_server():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((HOST, PORT))
        print(f"[UDP СЕРВЕР] Запущен на {HOST}:{PORT}")

        try:
            while True:
                data, client_address = server_socket.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"[UDP] Получено от {client_address}: {message}")

                if message == "Hello, server":
                    response = "Hello, client"
                    server_socket.sendto(response.encode('utf-8'), client_address)
                    print(f"[UDP] Отправлен ответ клиенту {client_address}: {response}")
        except KeyboardInterrupt:
            print("\n[UDP СЕРВЕР] Остановлен.")
        finally:
            server_socket.close()

    if __name__ == "__main__":
        run_udp_server()
    ```

    **udp_client.py**
    ```python
    import socket

    HOST = '127.0.0.1'
    PORT = 8081

    def run_udp_client():
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = "Hello, server"
        
        print(f"[UDP КЛИЕНТ] Отправка: {message}")
        client_socket.sendto(message.encode('utf-8'), (HOST, PORT))

        data, server_address = client_socket.recvfrom(1024)
        print(f"[UDP КЛИЕНТ] Ответ от сервера: {data.decode('utf-8')}")
        client_socket.close()

    if __name__ == "__main__":
        run_udp_client()
    ```

**Пример работы в терминале:**
```text
[UDP СЕРВЕР] Запущен на 127.0.0.1:8081
[UDP] Получено от ('127.0.0.1', 54455): Hello, server
[UDP] Отправлен ответ клиенту ('127.0.0.1', 54455): Hello, client

[UDP КЛИЕНТ] Отправка: Hello, server
[UDP КЛИЕНТ] Ответ от сервера: Hello, client
```

---

## Задание 2. Вычисления через TCP

**Описание протокола:** TCP (Transmission Control Protocol) требует предварительного установления соединения (`connect` и `accept`) и гарантирует надежную доставку потока байтов без потерь. Для работы используется `socket.SOCK_STREAM`. В данном задании реализовано решение квадратного уравнения.

!!! note "Особенности TCP"
    Дополнительные накладные расходы на установку соединения полностью окупаются надёжностью: все введенные пользователем параметры гарантированно дойдут до сервера, а результат вычисления — обратно.

??? info "Полный листинг кода калькулятора"
    **calc_server.py**
    ```python
    import socket
    import math

    HOST = '127.0.0.1'
    PORT = 8082

    def solve_quadratic(a, b, c):
        if a == 0:
            if b == 0:
                return "Нет решений (корректных)" if c != 0 else "Бесконечно много решений"
            return f"Линейное уравнение, корень: x = {-c / b}"
        
        discriminant = b**2 - 4*a*c
        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / (2 * a)
            x2 = (-b - math.sqrt(discriminant)) / (2 * a)
            return f"Два корня: x1 = {x1:.2f}, x2 = {x2:.2f}"
        elif discriminant == 0:
            x = -b / (2 * a)
            return f"Один корень: x = {x:.2f}"
        else:
            real = -b / (2 * a)
            imag = math.sqrt(abs(discriminant)) / (2 * a)
            return f"Комплексные корни: x1 = {real:.2f} + {imag:.2f}i, x2 = {real:.2f} - {imag:.2f}i"

    def run_calc_server():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"[TCP КАЛЬКУЛЯТОР] Сервер запущен на {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            print(f"[TCP КАЛЬКУЛЯТОР] Подключение от {addr}")
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    continue
                parts = list(map(float, data.split(',')))
                if len(parts) == 3:
                    result = solve_quadratic(*parts)
                    conn.sendall(result.encode('utf-8'))
            except Exception as e:
                conn.sendall(f"Error: {str(e)}".encode('utf-8'))
            finally:
                conn.close()

    if __name__ == "__main__":
        run_calc_server()
    ```

    **calc_client.py**
    ```python
    import socket

    HOST = '127.0.0.1'
    PORT = 8082

    def run_calc_client():
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        print("Решение квадратного уравнения ax^2 + bx + c = 0")
        a = input("Введите коэффициент a: ")
        b = input("Введите коэффициент b: ")
        c = input("Введите коэффициент c: ")

        payload = f"{a},{b},{c}"
        client_socket.sendall(payload.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        print(f"[РЕЗУЛЬТАТ ОТ СЕРВЕРА]: {response}")
        client_socket.close()

    if __name__ == "__main__":
        run_calc_client()
    ```

**Пример работы в терминале:**
```text
[TCP КАЛЬКУЛЯТОР] Сервер запущен на 127.0.0.1:8082
[TCP КАЛЬКУЛЯТОР] Подключение от ('127.0.0.1', 62051)

Решение квадратного уравнения ax^2 + bx + c = 0
Введите коэффициент a: 2
Введите коэффициент b: 3
Введите коэффициент c: 4
[РЕЗУЛЬТАТ ОТ СЕРВЕРА]: Комплексные корни: x1 = -0.75 + 1.20i, x2 = -0.75 - 1.20i
```

---

## Задание 3. Раздача HTML-страницы по HTTP

**Описание протокола:** HTTP (HyperText Transfer Protocol) — прикладной протокол, передающий данные в виде строго форматированного текста. Для отдачи статического файла сервер формирует строку статуса, заголовок `Content-Length` (на основе размера `index.html`), пустую строку и само тело файла.

!!! note "Структура ответа"
    Сервер читает файл `index.html`, подсчитывает размер сгенерированной строки в байтах и формирует ответ со статусом `HTTP/1.1 200 OK`.

??? info "Полный листинг HTTP-сервера"
    **http_server.py**
    ```python
    import socket
    import os

    HOST = '127.0.0.1'
    PORT = 8083

    def run_http_server():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[HTTP СЕРВЕР] Доступен по адресу: http://{HOST}:{PORT}")

        while True:
            client_conn, client_addr = server_socket.accept()
            try:
                request = client_conn.recv(1024).decode('utf-8')
                print(f"[HTTP] Запрос от {client_addr}")

                if os.path.exists("index.html"):
                    with open("index.html", "r", encoding="utf-8") as f:
                        html_content = f.read()
                    
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html; charset=UTF-8\r\n"
                        f"Content-Length: {len(html_content.encode('utf-8'))}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                        + html_content
                    )
                else:
                    body = "<h1>404 Not Found</h1>"
                    response = (
                        "HTTP/1.1 404 Not Found\r\n"
                        "Content-Type: text/html; charset=UTF-8\r\n"
                        f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                        "Connection: close\r\n\r\n" + body
                    )

                client_conn.sendall(response.encode('utf-8'))
            finally:
                client_conn.close()

    if __name__ == "__main__":
        run_http_server()
    ```

    **index.html**
    ```html
    <!DOCTYPE html>
    <html>
    <head><title>Lab 1 - Task 3</title></head>
    <body>
        <h1>Привет от HTTP сервера!</h1>
        <p>Эта страница успешно загружена из файла index.html.</p>
    </body>
    </html>
    ```

**Пример работы в терминале:**
```text
[HTTP СЕРВЕР] Доступен по адресу: http://127.0.0.1:8083
[HTTP] Запрос от ('127.0.0.1', 62792)
[HTTP] Запрос от ('127.0.0.1', 51171)
```

---

## Задание 4. Чат на сокетах (Многопользовательский)

**Описание архитектуры:** Реализован многопользовательский чат на протоколе TCP. Для одновременного обслуживания нескольких клиентов используется библиотека `threading`. Сервер держит список активных подключений в потокобезопасной коллекции и рассылает входящие сообщения всем участникам (Broadcast), кроме самого отправителя. Клиент реализует фоновый поток для асинхронного приема сообщений без блокировки метода `input()`.

!!! warning "Синхронизация потоков"
    Для безопасного изменения списка клиентов при параллельных подключениях обязательно используется `threading.Lock()`, предотвращающий состояние гонки (race condition).

??? info "Полный листинг чата"
    **server.py**
    ```python
    import socket
    import threading

    HOST = '127.0.0.1'
    PORT = 8084

    clients = []
    clients_lock = threading.Lock()

    def broadcast(message, exclude_socket=None):
        with clients_lock:
            for client in clients:
                if client != exclude_socket:
                    try:
                        client.sendall(message)
                    except:
                        pass

    def handle_client(client_socket, client_address):
        print(f"[ПОДКЛЮЧЕНИЕ] Установлено соединение с {client_address}")
        try:
            username_bytes = client_socket.recv(1024)
            if not username_bytes: return
            
            username = username_bytes.decode('utf-8').strip() or f"User_{client_address[1]}"
            print(f"[ПОЛЬЗОВАТЕЛЬ] {client_address} зарегистрирован как '{username}'")
            
            join_msg = f"[СЕРВЕР]: {username} присоединился к чату.\n"
            broadcast(join_msg.encode('utf-8'), exclude_socket=client_socket)

            while True:
                data = client_socket.recv(1024)
                if not data: break
                
                message_text = data.decode('utf-8').strip()
                if message_text.lower() == 'exit': break

                formatted_msg = f"[{username}]: {message_text}\n"
                print(f"[{username}]: {message_text}")
                broadcast(formatted_msg.encode('utf-8'), exclude_socket=client_socket)
        except ConnectionResetError:
            pass
        finally:
            with clients_lock:
                if client_socket in clients:
                    clients.remove(client_socket)
            client_socket.close()
            
            print(f"[ОТКЛЮЧЕНИЕ] {client_address} отключился.")
            broadcast(f"[СЕРВЕР]: {username} покинул чат.\n".encode('utf-8'))

    def run_server():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[ЧАТ СЕРВЕР] Запущен на {HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            with clients_lock:
                clients.append(client_socket)
            
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()

    if __name__ == "__main__":
        run_server()
    ```

    **client.py**
    ```python
    import socket
    import threading
    import sys

    HOST = '127.0.0.1'
    PORT = 8084

    def receive_messages(sock):
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    print("\n[Соединение с сервером закрыто]")
                    break
                sys.stdout.write('\r\033[K')
                sys.stdout.write(data.decode('utf-8'))
                sys.stdout.write("Вы: ")
                sys.stdout.flush()
            except Exception:
                print("\n[Ошибка связи с сервером]")
                break

    def run_client():
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((HOST, PORT))
        except ConnectionRefusedError:
            return

        username = input("Введите ваше имя для входа в чат: ").strip() or "Guest"
        client_socket.sendall(username.encode('utf-8'))

        print("\n[УСПЕХ] Вы в чате! Для выхода введите 'exit'.\n")

        recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        recv_thread.daemon = True
        recv_thread.start()

        try:
            while True:
                message = input("Вы: ")
                if not message.strip(): continue
                
                client_socket.sendall(message.encode('utf-8'))
                if message.lower() == 'exit': break
        except KeyboardInterrupt:
            print("\nВыход из чата...")
        finally:
            client_socket.close()

    if __name__ == "__main__":
        run_client()
    ```

**Пример работы в терминале:**
```text
[ЧАТ СЕРВЕР] Запущен на 127.0.0.1:8084
[ПОДКЛЮЧЕНИЕ] Установлено соединение с ('127.0.0.1', 50202)
[ПОЛЬЗОВАТЕЛЬ] ('127.0.0.1', 50202) зарегистрирован как 'rap'
[ПОДКЛЮЧЕНИЕ] Установлено соединение с ('127.0.0.1', 50233)
[ПОЛЬЗОВАТЕЛЬ] ('127.0.0.1', 50233) зарегистрирован как 'bobik'
[rap]: че как?
[bobik]: ништяк, бро

---
Введите ваше имя для входа в чат: rap

[УСПЕХ] Вы в чате! Для выхода введите 'exit'.

[СЕРВЕР]: bobik присоединился к чату.
Вы: че как?
[bobik]: ништяк, бро

---
Введите ваше имя для входа в чат:bobik

[УСПЕХ] Вы в чате! Для выхода введите 'exit'.

[rap]: че как?
Вы: ништяк, бро
```

---

## Задание 5. Простой веб-сервер (GET/POST)

**Описание архитектуры:** Разработан веб-сервер для обработки HTTP-запросов, который ведёт журнал оценок. Запрос разбирается вручную (извлечение метода и тела). Данные хранятся не в виде простого текстового лога, а структурированно — группируются по дисциплинам в словаре `grades_db`.

| Метод | URL | Описание |
|-------|-----|----------|
| GET   | `/` | Отдает HTML-страницу со списком всех дисциплин, оценок и формой |
| POST  | `/` | Парсит тело запроса, сохраняет новую оценку и обновляет страницу |

??? info "Полный листинг веб-сервера"
    **web_server.py**
    ```python
    import socket
    from urllib.parse import parse_qs

    HOST = '127.0.0.1'
    PORT = 8085

    grades_db = {
        "Математический анализ": [5, 4],
        "Веб-программирование": [5, 5]
    }

    def render_html():
        items_html = ""
        for discipline, grades in grades_db.items():
            grades_str = ", ".join(map(str, grades))
            items_html += f"<li><b>{discipline}</b>: Оценки: [{grades_str}]</li>"
        
        if not items_html:
            items_html = "<li>Журнал пока пуст.</li>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Журнал оценок</title>
        </head>
        <body>
            <h1>Журнал успеваемости студентов</h1>
            <ul>
                {items_html}
            </ul>
            <hr>
            <h2>Добавить оценку</h2>
            <form method="POST" action="/">
                <label>Дисциплина: <input type="text" name="discipline" required></label><br><br>
                <label>Оценка (число): <input type="number" name="grade" min="1" max="5" required></label><br><br>
                <button type="submit">Отправить</button>
            </form>
        </body>
        </html>
        """

    def run_web_server():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[ВЕБ-СЕРВЕР ЖУРНАЛА] Запущен: http://{HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            try:
                request_data = conn.recv(4096).decode('utf-8')
                if not request_data:
                    conn.close()
                    continue

                lines = request_data.split('\r\n')
                method = lines[0].split(' ')[0]

                if method == 'POST':
                    body_index = request_data.find('\r\n\r\n')
                    if body_index != -1:
                        parsed_body = parse_qs(request_data[body_index+4:])
                        discipline = parsed_body.get('discipline', [''])[0].strip()
                        grade_str = parsed_body.get('grade', [''])[0].strip()

                        if discipline and grade_str.isdigit():
                            grades_db.setdefault(discipline, []).append(int(grade_str))

                html_content = render_html()
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html; charset=UTF-8\r\n"
                    f"Content-Length: {len(html_content.encode('utf-8'))}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    + html_content
                )
                conn.sendall(response.encode('utf-8'))
            except Exception as e:
                print(f"[ОШИБКА ВЕБ-СЕРВЕРА]: {e}")
            finally:
                conn.close()

    if __name__ == "__main__":
        run_web_server()
    ```

**Пример работы в терминале:**
```text
[ВЕБ-СЕРВЕР ЖУРНАЛА] Запущен: http://127.0.0.1:8085
```
# ЛР1. Работа с сокетами

Востров Илья, группа K3339. Вариант 2 (порядковый номер — 6): **решение квадратного уравнения**.

## Задание 1. Обмен сообщениями по UDP

Клиент отправляет серверу сообщение `Hello, server`, сервер печатает его и отвечает `Hello, client`. UDP не устанавливает соединение, поэтому на сервере нет `listen()` и `accept()`: сокет просто привязывается к адресу (`bind`) и принимает датаграммы `recvfrom()`, а ответ отправляется `sendto()` по адресу, полученному вместе с датаграммой.

### Сервер

```python
import socket

HOST = '0.0.0.0'      # слушаем все сетевые интерфейсы
PORT = 9095
BUFFER_SIZE = 1024
REPLY = 'Hello, client'


def serve():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        print(f'UDP-сервер запущен на порту {PORT}')

        while True:
            data, client = server.recvfrom(BUFFER_SIZE)
            message = data.decode('utf-8')
            print(f'Получено от {client[0]}:{client[1]}: {message}')

            server.sendto(REPLY.encode('utf-8'), client)
            print(f'Отправлено в ответ: {REPLY}')


if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        print('\nСервер остановлен.')
```

### Клиент

```python
import socket

SERVER = ('127.0.0.1', 9095)
MESSAGE = 'Hello, server'
BUFFER_SIZE = 1024


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(5)          # чтобы не зависнуть без сервера
        client.sendto(MESSAGE.encode('utf-8'), SERVER)
        print(f'Отправлено серверу: {MESSAGE}')

        try:
            data, _ = client.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print('Ответа не дождались: сервер, похоже, не запущен.')
        else:
            print(f'Ответ сервера: {data.decode("utf-8")}')


if __name__ == '__main__':
    main()
```

### Работа в терминале

Сервер:

```text
UDP-сервер запущен на порту 9095
Получено от 127.0.0.1:56322: Hello, server
Отправлено в ответ: Hello, client
```

Клиент:

```text
Отправлено серверу: Hello, server
Ответ сервера: Hello, client
```

## Задание 2. Решение квадратного уравнения по TCP

Вариант 2. Клиент вводит коэффициенты `a`, `b`, `c` уравнения `a·x² + b·x + c = 0`, сервер вычисляет дискриминант `D = b² − 4ac` и корни:

* `D > 0` — два действительных корня `x₁,₂ = (−b ± √D) / 2a`;
* `D = 0` — один корень `x = −b / 2a`;
* `D < 0` — пара комплексно-сопряжённых корней;
* `a = 0` — уравнение вырождается в линейное.

Данные передаются одной строкой JSON на запрос. TCP гарантирует доставку и порядок, поэтому строка доходит целиком.

### Сервер

```python
import json
import math
import socket
from dataclasses import dataclass
from typing import Optional

HOST = '127.0.0.1'
PORT = 9096
BACKLOG = 5


@dataclass
class Outcome:
    """Результат решения уравнения."""
    discriminant: Optional[float]   # None — вырожденный (линейный) случай
    roots: list                     # корни: числа или комплексные


def solve(a, b, c):
    """Считает корни a*x^2 + b*x + c = 0.

    Возвращает (Outcome, None) при успехе или (None, текст_ошибки),
    если уравнение выродилось в тождество/противоречие.
    """
    if a == 0:
        if b == 0:
            return None, 'Уравнение вырождено: переменная x отсутствует'
        return Outcome(discriminant=None, roots=[-c / b]), None

    d = b * b - 4 * a * c
    if d > 0:
        root = math.sqrt(d)
        roots = [(-b - root) / (2 * a), (-b + root) / (2 * a)]
    elif d == 0:
        roots = [-b / (2 * a)]
    else:
        # дискриминант отрицателен: корни комплексные, сопряжённые
        real = -b / (2 * a) + 0.0
        imaginary = math.sqrt(-d) / (2 * a)
        roots = [complex(real, imaginary), complex(real, -imaginary)]

    return Outcome(discriminant=d, roots=roots), None


def handle(connection, address):
    """Обслуживает один клиентский запрос и закрывает соединение."""
    print(f'Подключился {address[0]}:{address[1]}')
    try:
        request = connection.makefile('r', encoding='utf-8').readline()
    except UnicodeDecodeError:
        response = {'error': 'Тело запроса должно быть текстом JSON'}
    else:
        if not request:
            return  # клиент закрыл соединение, ничего не прислав
        response = process(json.loads(request))
    connection.sendall((json.dumps(response, ensure_ascii=False) + '\n').encode('utf-8'))
    connection.close()


def process(payload):
    """Разбирает коэффициенты и превращает их в ответ для клиента."""
    try:
        a = float(payload['a'])
        b = float(payload['b'])
        c = float(payload['c'])
    except (KeyError, TypeError, ValueError):
        return {'error': 'Ожидались числа: a, b, c'}

    outcome, error = solve(a, b, c)
    if error:
        return {'error': error}
    return {
        'discriminant': outcome.discriminant,
        'roots': [str(root) for root in outcome.roots],   # комплексные как строки
    }


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(BACKLOG)
    print(f'Сервер вычислений запущен: {HOST}:{PORT}')

    while True:
        connection, address = server.accept()
        handle(connection, address)


if __name__ == '__main__':
    main()
```

### Клиент

```python
import json
import socket

SERVER = ('127.0.0.1', 9096)
PROMPT = 'Уравнение a*x^2 + b*x + c = 0'


def read_number(label):
    """Читает число с клавиатуры, допуская дробь через запятую."""
    while True:
        raw = input(f'{label} = ').strip().replace(',', '.')
        try:
            return float(raw)
        except ValueError:
            print('Нужно ввести число, попробуйте ещё раз.')


def main():
    print(PROMPT)
    a = read_number('a')
    b = read_number('b')
    c = read_number('c')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(SERVER)
        request = json.dumps({'a': a, 'b': b, 'c': c}) + '\n'
        client.sendall(request.encode('utf-8'))

        reply = client.makefile('r', encoding='utf-8').readline()

    if not reply:
        print('Сервер не ответил.')
        return

    answer = json.loads(reply)
    if 'error' in answer:
        print('Ошибка:', answer['error'])
        return

    if answer['discriminant'] is None:
        print('Уравнение линейное, единственный корень:', answer['roots'][0])
    else:
        print('Дискриминант:', answer['discriminant'])
        print('Корни:', ', '.join(answer['roots']))


if __name__ == '__main__':
    main()
```

### Работа в терминале

Клиент, два действительных корня (`x² − 5x + 6 = 0`):

```text
Уравнение a*x^2 + b*x + c = 0
a = 1
b = -5
c = 6
Дискриминант: 1.0
Корни: 2.0, 3.0
```

Клиент, комплексные корни (`x² + 1 = 0`):

```text
Уравнение a*x^2 + b*x + c = 0
a = 1
b = 0
c = 1
Дискриминант: -4.0
Корни: 1j, -1j
```

Сервер:

```text
Сервер вычислений запущен: 127.0.0.1:9096
Подключился 127.0.0.1:58180
Подключился 127.0.0.1:58181
```

## Задание 3. Раздача HTML-страницы по HTTP

Сервер при запуске читает файл `index.html` в байтах и отправляет его браузеру. Ответ собирается вручную: строка статуса `HTTP/1.1 200 OK`, заголовки `Content-Type` и `Content-Length`, пустая строка и тело. Длина тела учитывается в байтах — именно это значение указывает заголовок `Content-Length`. Для этого задания сервер умеет обрабатывать и несуществующий путь (возвращает 404).

### Сервер

```python
import socket
from http import HTTPStatus

HOST = '127.0.0.1'
PORT = 9085
PAGE_FILE = 'index.html'


class StaticServer:
    def __init__(self, host, port, page_path):
        self.host = host
        self.port = port
        with open(page_path, 'rb') as source:
            self.page = source.read()

    @staticmethod
    def _request_line(connection):
        """Читает из сокета первую строку запроса (до перевода строки)."""
        raw = b''
        while not raw.endswith(b'\r\n'):
            chunk = connection.recv(64)
            if not chunk:
                raise ConnectionError('соединение закрыто')
            raw += chunk
        first, _, _ = raw.partition(b'\r\n')
        return first.decode('utf-8').strip()

    @staticmethod
    def _response(status, body):
        """Собирает HTTP-ответ из кода статуса и тела в байтах."""
        head = (
            f'HTTP/1.1 {status.value} {status.phrase}\r\n'
            'Content-Type: text/html; charset=utf-8\r\n'
            f'Content-Length: {len(body)}\r\n'
            'Connection: close\r\n'
            '\r\n'
        )
        return head.encode('utf-8') + body

    def _handle(self, connection, address):
        try:
            line = self._request_line(connection)
            print(f'{address[0]}: {line}')

            parts = line.split()
            path = parts[1] if len(parts) > 1 else '/'

            if path in ('/', '/index.html'):
                reply = self._response(HTTPStatus.OK, self.page)
            else:
                body = ('<h1>404 — страница не найдена</h1>'
                        '<p><a href="/">Вернуться на главную</a></p>').encode('utf-8')
                reply = self._response(HTTPStatus.NOT_FOUND, body)

            connection.sendall(reply)
        except ConnectionError as error:
            print(f'{address[0]}: {error}')
        finally:
            connection.close()

    def serve_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen(5)
            print(f'HTTP-сервер запущен: http://{self.host}:{self.port}/')

            while True:
                connection, address = server.accept()
                self._handle(connection, address)


if __name__ == '__main__':
    StaticServer(HOST, PORT, PAGE_FILE).serve_forever()
```

### Работа в терминале

Запрос через curl:

```text
$ curl -i http://127.0.0.1:9085/
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 1762
Connection: close
```

Сервер:

```text
HTTP-сервер запущен: http://127.0.0.1:9085/
127.0.0.1: GET / HTTP/1.1
```

## Задание 4. Многопользовательский чат (TCP + threading)

Один и тот же `client.py` запускает каждый пользователь в своём терминале — роль клиента определяется не кодом, а именем, которое вводится первым сообщением. Сервер принимает имя, запоминает участника и пересылает каждое входящее сообщение всем, кроме автора. Выход — команда `/quit` или закрытие терминала.

Для одновременной работы с несколькими клиентами каждое подключение обслуживается в отдельном потоке (`threading`). Участники хранятся в словаре `{сокет: имя}`, а поскольку словарь разделяется между потоками, все операции с ним защищены блокировкой. Сообщения передаются построчно, поэтому на сервере для чтения используется сокетный файл `makefile('r')`.

### Сервер

    ```python
    import socket
    import threading

    HOST = '127.0.0.1'
    PORT = 9097


    class ChatRoom:
        """Активные участники чата.
        Словарь members разделяется между потоками, поэтому все операции
        с ним защищены блокировкой guard.
        """

        def __init__(self):
            self.members = {}          # {сокет: имя}
            self.guard = threading.Lock()

        def join(self, connection, nickname, address):
            with self.guard:
                self.members[connection] = nickname
            print(f'{nickname} вошёл в чат с {address[0]}:{address[1]}', flush=True)
            self.notify(f'* {nickname} присоединился', exclude=connection)

        def leave(self, connection, nickname):
            with self.guard:
                was_present = self.members.pop(connection, None) is not None
            connection.close()
            if was_present:
                print(f'{nickname} покинул чат', flush=True)
                self.notify(f'* {nickname} покинул чат', exclude=connection)

        def notify(self, text, exclude=None):
            """Шлёт строку всем участникам, кроме exclude."""
            with self.guard:
                targets = [conn for conn in self.members if conn != exclude]
            for target in targets:
                try:
                    target.sendall((text + '\n').encode('utf-8'))
                except OSError:
                    pass  # отвалившийся клиент уберёт сам себя в своём потоке


    room = ChatRoom()


    def chat_session(connection, address):
        reader = connection.makefile('r', encoding='utf-8')
        nickname = reader.readline().strip()
        if not nickname:
            connection.close()
            return

        room.join(connection, nickname, address)
        try:
            for line in reader:
                text = line.strip()
                if text == '/quit':
                    break
                if text:
                    print(f'{nickname}: {text}', flush=True)
                    room.notify(f'{nickname}: {text}', exclude=connection)
        finally:
            room.leave(connection, nickname)


    def main():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f'Чат-сервер запущен: {HOST}:{PORT}')

        while True:
            connection, address = server.accept()
            threading.Thread(
                target=chat_session, args=(connection, address), daemon=True
            ).start()


    if __name__ == '__main__':
        main()
    ```

### Клиент

    ```python
    import socket
    import threading

    SERVER = ('127.0.0.1', 9097)
    LEAVE_COMMAND = '/quit'


    def listener(reader):
        """Фоновая задача: выводит сообщения, которые приходят от сервера."""
        for line in reader:
            print(f'\r  {line.strip()}\n> ', end='', flush=True)
        print('\nСвязь с сервером прервана.')


    def main():
        nickname = input('Введите имя: ').strip()
        if not nickname:
            print('Имя не может быть пустым.')
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(SERVER)
            client.sendall((nickname + '\n').encode('utf-8'))

            threading.Thread(
                target=listener,
                args=(client.makefile('r', encoding='utf-8'),),
                daemon=True,
            ).start()

            print(f'Вы в чате {SERVER[0]}:{SERVER[1]}. Команда {LEAVE_COMMAND} — выход.')
            while True:
                text = input('> ').strip()
                # sendall отправляет сразу; буферизованный writer мог бы
                # отложить отправку до закрытия сокета
                if text == LEAVE_COMMAND:
                    client.sendall((LEAVE_COMMAND + '\n').encode('utf-8'))
                    break
                if text:
                    client.sendall((text + '\n').encode('utf-8'))

        print('Вы вышли из чата.')


    if __name__ == '__main__':
        main()
    ```

### Работа в терминале

Сервер:

```text
Чат-сервер запущен: 127.0.0.1:9097
Алиса вошёл в чат с 127.0.0.1:58187
Боб вошёл в чат с 127.0.0.1:58188
Алиса: Всем привет!
Боб: Привет, Алиса!
Алиса покинул чат
Боб покинул чат
```

Клиент Алиса (своё сообщение не приходит обратно — его видит только Боб):

```text
Введите имя: Алиса
Вы в чате 127.0.0.1:9097. Команда /quit — выход.
> Всем привет!
  Боб: Привет, Алиса!
> /quit
Вы вышли из чата.
```

## Задание 5. Веб-сервер GET/POST

`GET /` — сервер отдаёт HTML-страницу с формой и таблицей всех оценок. `POST /` — сервер разбирает тело формы (`discipline=...&grade=...`), сохраняет оценку и снова отдаёт страницу. Журнал хранится как `{дисциплина: [оценки]}` — у каждого предмета одна запись со списком всех его оценок, а не отдельная строка на каждую оценку. Для разбора тела формы написан собственный URL-декодер (`+` → пробел, `%XX` → байт), а вставляемые в страницу значения экранируются.

Соединения обрабатываются в потоках (пул `concurrent.futures`), чтобы медленный клиент не блокировал остальных. Неизвестный путь — 404, неподдерживаемый метод — 405.

### Сервер

    ```python
    import socket
    from concurrent.futures import ThreadPoolExecutor
    from html import escape
    from http import HTTPStatus

    HOST = '127.0.0.1'
    PORT = 9086


    def unquote(text):
        """Декодирует значения формы: '+' -> пробел, '%XX' -> байт"""
        decoded = bytearray()
        i = 0
        while i < len(text):
            if text[i] == '+':
                decoded.append(0x20)
                i += 1
            elif (
                text[i] == '%'
                and i + 2 < len(text)
                and all(c in '0123456789abcdefABCDEF' for c in text[i + 1:i + 3])
            ):
                decoded.append(int(text[i + 1:i + 3], 16))
                i += 3
            else:
                decoded.extend(text[i].encode('utf-8'))
                i += 1
        return decoded.decode('utf-8')


    def parse_form(raw):
        """Разбирает 'subject=Математика&grade=5&...' в словарь {поле: значение}."""
        fields = {}
        for pair in raw.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                fields[key] = unquote(value)
        return fields


    class GradebookServer:
        def __init__(self, host, port):
            self.host = host
            self.port = port
            self.grades = {}   # дисциплина -> список оценок

        def _read_request(self, connection):
            raw = b''
            while b'\r\n\r\n' not in raw:
                chunk = connection.recv(1024)
                if not chunk:
                    raise ConnectionError('запрос оборван')
                raw += chunk

            head, _, body = raw.partition(b'\r\n\r\n')
            parts = head.decode('utf-8').split()
            method = parts[0] if parts else 'GET'
            path = parts[1] if len(parts) > 1 else '/'

            headers = {}
            for line in head.decode('utf-8').split('\r\n')[1:]:
                if ':' in line:
                    name, value = line.split(':', 1)
                    headers[name.strip().lower()] = value.strip()

            # тело может прийти не за один recv — добираем до Content-Length
            length = int(headers.get('content-length', 0))
            while len(body) < length:
                chunk = connection.recv(1024)
                if not chunk:
                    break
                body += chunk
            return method, path, body[:length].decode('utf-8')

        @staticmethod
        def _response(status, body):
            payload = body.encode('utf-8')
            head = (
                f'HTTP/1.1 {status.value} {status.phrase}\r\n'
                'Content-Type: text/html; charset=utf-8\r\n'
                f'Content-Length: {len(payload)}\r\n'
                'Connection: close\r\n'
                '\r\n'
            )
            return head.encode('utf-8') + payload

        def handle_get(self):
            return self._response(HTTPStatus.OK, self.render_page())

        def handle_post(self, body):
            fields = parse_form(body)
            subject = fields.get('discipline', '').strip()
            grade = fields.get('grade', '').strip()

            if not subject or not grade:
                return self._response(
                    HTTPStatus.OK,
                    self.render_page(notice='Заполнены не все поля!'),
                )

            # оценки группируются по дисциплине: один ключ — все оценки предмета
            self.grades.setdefault(subject, []).append(grade)
            print(f'Внесено в журнал: {subject} — {grade}')
            return self._response(HTTPStatus.OK, self.render_page())

        def handle_connection(self, connection, address):
            try:
                method, path, body = self._read_request(connection)
                print(f'{address[0]}: {method} {path}')

                if path == '/' and method == 'GET':
                    response = self.handle_get()
                elif path == '/' and method == 'POST':
                    response = self.handle_post(body)
                elif path != '/':
                    response = self._response(
                        HTTPStatus.NOT_FOUND,
                        '<h1>404 — такой страницы нет</h1><p><a href="/">На главную</a></p>',
                    )
                else:
                    response = self._response(
                        HTTPStatus.METHOD_NOT_ALLOWED,
                        '<h1>405 — метод не поддерживается</h1>',
                    )

                connection.sendall(response)
            except ConnectionError as error:
                print(f'{address[0]}: {error}')
            finally:
                connection.close()

        def render_page(self, notice=''):
            rows = ''
            for subject, marks in self.grades.items():
                items = ''.join(f'<li>{escape(mark)}</li>' for mark in marks)
                rows += (
                    f'<tr><td>{escape(subject)}</td>'
                    f'<td><ol>{items}</ol></td>'
                    f'<td>{len(marks)}</td></tr>'
                )

            if rows:
                table = (
                    '<table>'
                    '<tr><th>Дисциплина</th><th>Оценки</th><th>Количество</th></tr>'
                    f'{rows}</table>'
                )
            else:
                table = '<p class="hint">Журнал пока пуст — добавьте первую оценку.</p>'

            alert = f'<p class="alert">{escape(notice)}</p>' if notice else ''
            return f'''<!DOCTYPE html>
        <html lang="ru">
        <head>
          <meta charset="utf-8">
          <title>Журнал успеваемости</title>
          <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 680px; margin: 40px auto; color: #2b2b2b; }}
            h1 {{ color: #0b5cad; }}
            form {{ background: #f2f6fb; padding: 16px; border-radius: 8px; }}
            input {{ padding: 6px 8px; margin-right: 8px; }}
            button {{ padding: 6px 14px; cursor: pointer; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 14px; }}
            th, td {{ border: 1px solid #b9c6d4; padding: 8px; text-align: left; }}
            th {{ background: #e7eef7; }}
            ol {{ margin: 0; padding-left: 18px; }}
            .alert {{ color: #c0392b; font-weight: bold; }}
            .hint {{ color: #7f8c8d; }}
          </style>
        </head>
        <body>
          <h1>Журнал успеваемости</h1>
          {alert}
          <form method="post" action="/">
            <p>Дисциплина: <input name="discipline" placeholder="например, Математика" required></p>
            <p>Оценка: <input name="grade" placeholder="например, 5" required></p>
            <p><button type="submit">Внести оценку</button></p>
          </form>
          <h2>Все оценки по дисциплинам</h2>
          {table}
        </body>
        </html>'''

        def serve_forever(self):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen(5)
            print(f'Веб-сервер журнала запущен: http://{self.host}:{self.port}/')

            # пул потоков, чтобы один медленный клиент не блокировал других
            with ThreadPoolExecutor(max_workers=8) as pool:
                while True:
                    connection, address = server.accept()
                    pool.submit(self.handle_connection, connection, address)


    if __name__ == '__main__':
        GradebookServer(HOST, PORT).serve_forever()
    ```

### Работа в терминале

Добавление оценок:

```text
$ curl -d "discipline=Математика&grade=5" http://127.0.0.1:9086/
$ curl -d "discipline=Математика&grade=4" http://127.0.0.1:9086/
$ curl -d "discipline=Физика&grade=3" http://127.0.0.1:9086/
```

Сервер (оценки одного предмета копятся в одну запись):

```text
Веб-сервер журнала запущен: http://127.0.0.1:9086/
127.0.0.1: POST /
Внесено в журнал: Математика — 5
127.0.0.1: POST /
Внесено в журнал: Математика — 4
127.0.0.1: POST /
Внесено в журнал: Физика — 3
```

Строки таблицы на странице журнала:

```text
<tr><td>Математика</td><td><ol><li>5</li><li>4</li></ol></td><td>2</td></tr>
<tr><td>Физика</td><td><ol><li>3</li></ol></td><td>1</td></tr>
```

Неизвестный путь и метод:

```text
$ curl -o /dev/null -w "%{http_code}" http://127.0.0.1:9086/nope
404
$ curl -X PUT -o /dev/null -w "%{http_code}" http://127.0.0.1:9086/
405
```

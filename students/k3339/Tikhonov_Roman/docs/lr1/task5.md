# Задание 5. Веб-сервер (журнал оценок)

## Протокол

Веб-сервер поверх **TCP** обрабатывает HTTP-запросы GET и POST. HTTP-запрос
разбирается вручную: определяется метод и путь, для POST читается тело по заголовку
`Content-Length`. Сервер хранит оценки в словаре «дисциплина - список оценок» и
отдаёт их в виде HTML-страницы.

| Параметр  | Значение                        |
|-----------|---------------------------------|
| Протокол  | HTTP поверх TCP (`SOCK_STREAM`) |
| Адрес     | `127.0.0.1`                     |
| Порт      | `8085`                          |
| Обработка | последовательная (без потоков)  |

## Эндпоинты

| Метод  | URL       | Описание                                                      |
|--------|-----------|---------------------------------------------------------------|
| `POST` | `/grade`  | Сохранить оценку. Тело: `дисциплина=Математика&оценка=5`      |
| `GET`  | `/`       | HTML-страница со списком оценок, сгруппированных по предметам |
| `GET`  | `/grades` | То же, что `/`                                                |

## Модель данных

Журнал — словарь `grades` вида «дисциплина список оценок». Группировка по предмету:
две оценки по «Математике» хранятся как одна запись `Математика: [5, 4]`, а не как
две отдельные строки.

## Код сервера

    ```python
    import socket
    from html import escape
    from urllib.parse import unquote

    HOST = '127.0.0.1'
    PORT = 8085

    grades = {}  # дисциплина -> список оценок


    def parse_body(body):
        pairs = body.split('&')
        result = {}
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                result[unquote(key)] = unquote(value)
        return result


    def handle_post(body):
        data = parse_body(body)
        subject = data.get('дисциплина', '')
        mark = data.get('оценка', '')
        if not subject or not mark:
            return '400 Bad Request', 'Нет дисциплины или оценки'

        if subject in grades:
            grades[subject].append(mark)
        else:
            grades[subject] = [mark]

        return '200 OK', f'Оценка {mark} по предмету "{subject}" сохранена'


    def build_page():
        rows = ''
        items = list(grades.items())
        if not items:
            rows = '<p>Оценок пока нет.</p>'
        else:
            for subject, marks in items:
                rows += f'<li>{escape(subject)}: {", ".join(escape(m) for m in marks)}</li>'
            rows = '<ul>' + rows + '</ul>'

        return '<h1>Журнал оценок</h1><h2>Все оценки</h2>' + rows


    def handle_request(conn, data):
        lines = data.split('\r\n')
        first = lines[0].split()
        if len(first) < 2:
            conn.sendall(b'HTTP/1.1 400 Bad Request\r\n\r\n')
            return

        method, path = first[0], first[1]
        body = ''
        if method == 'POST':
            content_length = 0
            for line in lines[1:]:
                if line.lower().startswith('content-length:'):
                    content_length = int(line.split(':', 1)[1].strip())
            if content_length:
                body = data.split('\r\n\r\n', 1)[1][:content_length]

        if method == 'GET' and path in ('/', '/grades'):
            page = build_page()
            status = '200 OK'
            response_body = page.encode('utf-8')
        elif method == 'POST' and path == '/grade':
            status, message = handle_post(body)
            response_body = message.encode('utf-8')
        else:
            status = '404 Not Found'
            response_body = 'Страница не найдена'.encode('utf-8')

        header = (f'HTTP/1.1 {status}\r\nContent-Type: text/html; charset=utf-8\r\n'
                  f'Content-Length: {len(response_body)}\r\nConnection: close\r\n\r\n')
        conn.sendall(header.encode('utf-8') + response_body)


    def handle_client(conn, address):
        data = conn.recv(65536).decode('utf-8', errors='replace')
        if data:
            print(f'Запрос от {address}: {data.splitlines()[0]}')
            handle_request(conn, data)
        conn.close()


    def main():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f'Сервер запущен по адресу http://{HOST}:{PORT}')

        while True:
            conn, address = server_socket.accept()
            handle_client(conn, address)


    if __name__ == '__main__':
        main()
    ```

## Пример работы в терминале

**Окно 1 — сервер:**

```
> python src/task5/server.py
Сервер запущен по адресу http://127.0.0.1:8085
Запрос от ('127.0.0.1', 52001): POST /grade HTTP/1.1
Запрос от ('127.0.0.1', 52002): POST /grade HTTP/1.1
Запрос от ('127.0.0.1', 52003): GET / HTTP/1.1
```

**Добавление оценок (curl):**

```
> curl -X POST --data "дисциплина=Математика&оценка=5" http://127.0.0.1:8085/grade
Оценка 5 по предмету "Математика" сохранена
> curl -X POST --data "дисциплина=Математика&оценка=4" http://127.0.0.1:8085/grade
Оценка 4 по предмету "Математика" сохранена
> curl -X POST --data "дисциплина=Физика&оценка=5" http://127.0.0.1:8085/grade
Оценка 5 по предмету "Физика" сохранена
```

**GET `/`:** страница показывает `Математика: 5, 4` и `Физика: 5` — по одной записи на предмет.

## Запуск

1. Терминал 1: `python src/task5/server.py`
2. Добавить оценки через `curl` или форму, открыть `http://127.0.0.1:8085/`.
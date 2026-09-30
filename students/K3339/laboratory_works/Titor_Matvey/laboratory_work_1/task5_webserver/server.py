import socket
from urllib.parse import parse_qs

HOST = 'localhost'
PORT = 8081

grades = {}


def read_request(conn):
    buffer = b''
    while b'\r\n\r\n' not in buffer:
        chunk = conn.recv(1024)
        if not chunk:
            raise ConnectionError
        buffer += chunk

    headers_part, _, body = buffer.partition(b'\r\n\r\n')
    lines = headers_part.decode().split('\r\n')

    method, path, version = lines[0].split(' ')

    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.lower()] = value.strip()

    content_length = int(headers.get('content-length', 0))
    while len(body) < content_length:
        chunk = conn.recv(1024)
        if not chunk:
            break
        body += chunk

    return method, path, body[:content_length]


def make_response(status, body):
    body = body.encode()
    head = (
        f'HTTP/1.1 {status}\r\n'
        'Content-Type: text/html; charset=utf-8\r\n'
        f'Content-Length: {len(body)}\r\n'
        'Connection: close\r\n'
        '\r\n'
    )
    return head.encode() + body


def build_page():
    rows = ''
    for discipline, marks in grades.items():
        marks_html = ''.join(f'<li>{mark}</li>' for mark in marks)
        rows += f'<tr><td>{discipline}</td><td><ul>{marks_html}</ul></td><td>{len(marks)}</td></tr>'

    if grades:
        table = f"<table border='1'><tr><th>Дисциплина</th><th>Оценки</th><th>Всего</th></tr>{rows}</table>"
    else:
        table = '<p>Журнал пуст — добавьте первую оценку.</p>'

    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <form method="post" action="/">
        Дисциплина: <input name="discipline"><br><br>
        Оценка: <input name="grade"><br><br>
        <button type="submit">Добавить</button>
    </form>
    <h2>Оценки по дисциплинам</h2>
    {table}
</body>
</html>'''


def handle_connection(conn, address):
    try:
        method, path, body = read_request(conn)
        print(f'{address}: {method} {path}')

        if path != '/':
            response = make_response('404 Not Found', '<h1>404 — страница не найдена</h1><p><a href="/">На главную</a></p>')
        elif method == 'GET':
            response = make_response('200 OK', build_page())
        elif method == 'POST':
            fields = parse_qs(body.decode())
            discipline = fields.get('discipline', [''])[0].strip()
            grade = fields.get('grade', [''])[0].strip()

            if discipline and grade:
                grades.setdefault(discipline, []).append(grade)
                print(f'Сохранено: {discipline} — {grade}')
                response = make_response('200 OK', build_page())
            else:
                response = make_response('200 OK', '<h1>Заполните оба поля</h1><p><a href="/">Вернуться</a></p>')
        else:
            response = make_response('405 Method Not Allowed', '<h1>Метод не поддерживается</h1>')

        conn.sendall(response)
    except ConnectionError:
        print(f'{address}: клиент отключился, не прислав запрос')
    finally:
        conn.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'Веб-сервер запущен: http://{HOST}:{PORT}/')

while True:
    conn, address = server_socket.accept()
    handle_connection(conn, address)

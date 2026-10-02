import socket
from html import escape
from urllib.parse import unquote

HOST = '127.0.0.1'
PORT = 8085

grades = {}  # дисциплина-список оценок


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

    return '''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Журнал оценок</title></head>
<body>
<h1>Журнал оценок</h1>
<form method="post" action="/grade">
    <input type="text" name="дисциплина" placeholder="Дисциплина" required>
    <input type="text" name="оценка" placeholder="Оценка" required>
    <button type="submit">Добавить</button>
</form>
<h2>Все оценки</h2>
''' + rows + '''
</body>
</html>'''


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

    header = f'HTTP/1.1 {status}\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {len(response_body)}\r\nConnection: close\r\n\r\n'
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


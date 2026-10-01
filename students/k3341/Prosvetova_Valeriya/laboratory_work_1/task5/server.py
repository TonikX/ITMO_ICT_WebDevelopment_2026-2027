import socket
from urllib.parse import parse_qs

HOST = 'localhost'
PORT = 9005

# Журнал оценок: дисциплина -> список оценок
grades = {}


def parse_request(raw_request: str):
    """Разбирает сырой HTTP-запрос на метод, путь и тело."""
    lines = raw_request.split('\r\n')
    method, path, _ = lines[0].split(' ')

    headers = {}
    body_start = 0
    for i, line in enumerate(lines[1:], start=1):
        if line == '':
            body_start = i + 1
            break
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()

    body = '\r\n'.join(lines[body_start:]) if body_start else ''
    return method, path, headers, body


def render_grades_page() -> str:
    rows = ''
    for subject, subject_grades in grades.items():
        grades_str = ', '.join(str(g) for g in subject_grades)
        rows += f"<tr><td>{subject}</td><td>{grades_str}</td></tr>\n"

    if not rows:
        rows = '<tr><td colspan="2">Оценок пока нет</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
    <h2>Добавить оценку</h2>
    <form method="POST" action="/">
        Дисциплина: <input type="text" name="subject"><br><br>
        Оценка: <input type="text" name="grade"><br><br>
        <input type="submit" value="Отправить">
    </form>
</body>
</html>"""


def build_response(status: str, body: str) -> bytes:
    body_bytes = body.encode('utf-8')
    response = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode('utf-8') + body_bytes
    return response


def handle_request(raw_request: str) -> bytes:
    if not raw_request:
        return build_response("400 Bad Request", "<h1>400 Bad Request</h1>")

    method, path, headers, body = parse_request(raw_request)
    print(f"{method} {path}")

    if method == 'POST':
        content_length = int(headers.get('content-length', 0))
        # Тело могло быть считано не полностью в одном recv - для
        # учебного примера полагаем, что оно умещается в один пакет.
        params = parse_qs(body[:content_length])
        subject = params.get('subject', [''])[0].strip()
        grade = params.get('grade', [''])[0].strip()

        if subject and grade:
            grades.setdefault(subject, []).append(grade)

        return build_response("200 OK", render_grades_page())

    elif method == 'GET':
        return build_response("200 OK", render_grades_page())

    else:
        return build_response("405 Method Not Allowed", "<h1>405 Method Not Allowed</h1>")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Веб-сервер журнала оценок запущен на {HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        raw_request = conn.recv(4096).decode('utf-8', errors='ignore')
        response = handle_request(raw_request)
        conn.sendall(response)
        conn.close()


if __name__ == '__main__':
    main()

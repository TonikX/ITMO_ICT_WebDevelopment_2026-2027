import socket
from urllib.parse import parse_qs

HOST = 'localhost'
PORT = 8084

journal = {}
ALLOWED_GRADES = {"2", "3", "4", "5"}

INDEX_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>

    <form method="POST" action="/">
        <label>Дисциплина: <input type="text" name="subject" required></label><br>
        <label>Оценка: <input type="text" name="grade" required></label><br>
        <button type="submit">Добавить</button>
    </form>

    <h2>Все оценки</h2>
    {TABLE}
</body>
</html>
"""


def render_table():
    if not journal:
        return "<p>Пока нет ни одной оценки.</p>"
    rows = ""
    for subject, grades in journal.items():
        rows += f"<tr><td>{subject}</td><td>{', '.join(grades)}</td></tr>"
    return (
        "<table border='1' cellpadding='5'>"
        "<tr><th>Дисциплина</th><th>Оценки</th></tr>"
        + rows +
        "</table>"
    )

def send_response(connection, status, body):
    body_bytes = body.encode('utf-8')
    response = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode('utf-8') + body_bytes
    connection.sendall(response)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"HTTP сервер запущен: http://{HOST}:{PORT}/")

while True:
    connection, address = server_socket.accept()
    print(f"Подключение от {address}")

    data = b""
    while b"\r\n\r\n" not in data:
        chunk = connection.recv(4096)
        if not chunk:
            break
        data += chunk
    head, _, body = data.partition(b"\r\n\r\n")

    content_length = 0
    for line in head.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            content_length = int(line.split(b":", 1)[1].strip())
            break
    while len(body) < content_length:
        chunk = connection.recv(4096)
        if not chunk:
            break
        body += chunk

    request_line = head.split(b"\r\n")[0].decode('utf-8', errors='ignore')
    parts = request_line.split()
    method = parts[0] if len(parts) > 0 else ""
    path = parts[1] if len(parts) > 1 else "/"

    print(f"{method} {path}")

    if method == "POST":
        params = parse_qs(body.decode('utf-8', errors='ignore'))
        subject = params.get("subject", [""])[0].strip()
        grade = params.get("grade", [""])[0].strip()

        if subject and grade in ALLOWED_GRADES:
            journal.setdefault(subject, []).append(grade)

        redirect = (
            "HTTP/1.1 303 See Other\r\n"
            "Location: /\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8')
        connection.sendall(redirect)
    elif method == "GET":
        html = INDEX_HTML.replace("{TABLE}", render_table())
        send_response(connection, "200 OK", html)
    else:
        send_response(connection, "405 Method Not Allowed", "<h1>405</h1>")
    connection.close()
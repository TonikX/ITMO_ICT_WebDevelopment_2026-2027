import socket
from collections import defaultdict
from urllib.parse import parse_qs

grades = defaultdict(list)


def render_page():
    rows = "".join(
        f"<li>{subject}: {', '.join(values)}</li>"
        for subject, values in grades.items()
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <ul>{rows}</ul>
    <form method="POST" action="/">
        Дисциплина: <input name="subject">
        Оценка: <input name="grade">
        <button>Сохранить</button>
    </form>
</body>
</html>
"""


def send_response(connection, html):
    body = html.encode("utf-8")
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    connection.sendall(headers.encode("utf-8") + body)


def read_request(connection):
    raw = b""
    while b"\r\n\r\n" not in raw:
        chunk = connection.recv(1024)
        if not chunk:
            break
        raw += chunk

    header_part, body = raw.split(b"\r\n\r\n", 1)
    lines = header_part.decode("utf-8").split("\r\n")
    method, path, _ = lines[0].split()

    content_length = 0
    for line in lines[1:]:
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1])

    while len(body) < content_length:
        body += connection.recv(content_length - len(body))

    return method, path, body.decode("utf-8")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8080))
server_socket.listen(1)

while True:
    connection, _ = server_socket.accept()
    method, path, body = read_request(connection)
    if method == "POST":
        form = parse_qs(body)
        subject = form.get("subject", [""])[0]
        grade = form.get("grade", [""])[0]
        if subject and grade:
            grades[subject].append(grade)
    send_response(connection, render_page())
    connection.close()

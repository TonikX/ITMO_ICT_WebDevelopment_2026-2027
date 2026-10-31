import html
import socket
from urllib.parse import parse_qs

HOST = "localhost"
PORT = 9005

journal = {}


def read_request(client_connection):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = client_connection.recv(1024)
        if not chunk:
            return None
        data += chunk
    head, body = data.split(b"\r\n\r\n", 1)
    lines = head.decode().split("\r\n")

    method, path, _ = lines[0].split(" ")

    content_length = 0
    for line in lines[1:]:
        header_name, header_value = line.split(":", 1)
        if header_name.strip().lower() == "content-length":
            content_length = int(header_value)

    while len(body) < content_length:
        chunk = client_connection.recv(1024)
        if not chunk:
            break
        body += chunk
    return method, path, body.decode()


def journal_page():
    rows = ""
    for discipline, grades in journal.items():
        rows += f"        <tr><td>{html.escape(discipline)}</td><td>{html.escape(', '.join(grades))}</td></tr>\n"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <table border="1">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
{rows}    </table>
    <h2>Добавить оценку</h2>
    <form method="post" action="/">
        <p>Дисциплина: <input name="discipline" required></p>
        <p>Оценка: <input name="grade" required></p>
        <button type="submit">Сохранить</button>
    </form>
</body>
</html>
"""


def send_response(client_connection, status, body):
    body = body.encode()
    head = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    client_connection.sendall(head.encode() + body)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Веб-сервер запущен: http://{HOST}:{PORT}/")

try:
    while True:
        client_connection, client_address = server_socket.accept()
        request = read_request(client_connection)

        if request:
            method, path, body = request
            print(f"{method} {path} от {client_address}")

            if path != "/":
                send_response(client_connection, "404 Not Found", "<h1>404 Not Found</h1>")
            elif method == "GET":
                send_response(client_connection, "200 OK", journal_page())
            elif method == "POST":
                form = parse_qs(body)
                discipline = form.get("discipline", [""])[0].strip()
                grade = form.get("grade", [""])[0].strip()
                if discipline and grade:
                    journal.setdefault(discipline, []).append(grade)
                    print(f"Записана оценка: {discipline} — {grade}")
                    send_response(client_connection, "200 OK", journal_page())
                else:
                    send_response(client_connection, "400 Bad Request", "<h1>Нужно указать дисциплину и оценку</h1>")
            else:
                send_response(client_connection, "501 Not Implemented", "<h1>Поддерживаются только GET и POST</h1>")

        client_connection.close()
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()

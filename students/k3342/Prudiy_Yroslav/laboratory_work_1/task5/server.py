import html
import socket
from pathlib import Path
from urllib.parse import parse_qs

HOST, PORT = "127.0.0.1", 5001
TEMPLATE = Path(__file__).with_name("index.html")


def render_page(grades, notice=""):
    rows = "".join(
        f"<tr><td>{html.escape(subject)}</td><td>{', '.join(map(str, values))}</td>"
        f"<td>{sum(values) / len(values):.2f}</td></tr>"
        for subject, values in sorted(grades.items())
    ) or '<tr><td colspan="3">Оценок пока нет</td></tr>'

    page = TEMPLATE.read_text(encoding="utf-8")

    return page.replace("{{NOTICE}}", notice).replace("{{GRADE_ROWS}}", rows).encode()


def read_request(client):
    request = b""

    while b"\r\n\r\n" not in request:
        request += client.recv(4096)

    head, body = request.split(b"\r\n\r\n", 1)
    lines = head.decode().split("\r\n")

    method, path, _ = lines[0].split()
    headers = dict(line.split(": ", 1) for line in lines[1:] if ": " in line)
    length = int(headers.get("Content-Length", 0))

    while len(body) < length:
        body += client.recv(4096)

    return method, path, body


def send_page(client, status, body):
    headers = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode()

    client.sendall(headers + body)


def run_server():
    grades = {}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"http://{HOST}:{PORT}")

        while True:
            client, _ = server.accept()

            with client:
                try:
                    method, path, body = read_request(client)

                    if path != "/" or method not in ("GET", "POST"):
                        send_page(client, "404 Not Found", b"Not found")
                        continue

                    notice = ""

                    if method == "POST":
                        form = parse_qs(body.decode())

                        subject = form["subject"][0].strip()
                        grade = int(form["grade"][0])

                        if not subject or grade not in range(2, 6):
                            raise ValueError

                        grades.setdefault(subject, []).append(grade)
                        notice = "<p>Оценка сохранена</p>"

                    send_page(client, "200 OK", render_page(grades, notice))

                except (KeyError, ValueError):
                    send_page(client, "400 Bad Request", "Некорректные данные".encode())


if __name__ == "__main__":
    run_server()

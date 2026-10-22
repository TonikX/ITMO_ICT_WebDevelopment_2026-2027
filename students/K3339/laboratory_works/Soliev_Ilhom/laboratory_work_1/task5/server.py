import json
import socket
from html import escape
from pathlib import Path
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8081
DIRECTORY = Path(__file__).parent

def read_request(connection):
    stream = connection.makefile("rb")
    method, path, _ = stream.readline().decode().split()

    headers = {}
    while line := stream.readline():
        if line == b"\r\n":
            break
        name, value = line.decode().split(":", 1)
        headers[name.lower()] = value.strip()

    body = stream.read(int(headers.get("content-length", 0)))
    return method, path, body


def save_grade(subject, grade):
    file = DIRECTORY / "grades.json"
    grades = json.loads(file.read_text(encoding="utf-8"))
    grades.setdefault(subject, []).append(grade)
    file.write_text(json.dumps(grades, ensure_ascii=False, indent=2), encoding="utf-8")


def page():
    grades = json.loads((DIRECTORY / "grades.json").read_text(encoding="utf-8"))
    rows = "".join(
        f"<tr><td>{escape(subject)}</td><td>{escape(', '.join(marks))}</td></tr>"
        for subject, marks in grades.items()
    )
    html = (DIRECTORY / "index.html").read_text(encoding="utf-8")
    return html.replace("{{rows}}", rows)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()

    while True:
        connection, _ = server.accept()
        with connection:
            method, path, body = read_request(connection)

            if method == "POST":
                form = parse_qs(body.decode())
                save_grade(form["subject"][0], form["grade"][0])

            response_body = page().encode("utf-8")
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/html; charset=utf-8\r\n"
                + f"Content-Length: {len(response_body)}\r\n\r\n".encode()
                + response_body
            )
            connection.sendall(response)

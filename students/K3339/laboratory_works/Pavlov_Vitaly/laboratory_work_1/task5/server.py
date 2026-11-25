import html
import socket
from urllib.parse import parse_qs

HOST = "127.0.0.1"
PORT = 8085


class MyHTTPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.grades = {}

    def serve_forever(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        print(f"Сервер запущен: http://{self.host}:{self.port}/")
        while True:
            conn, address = server.accept()
            try:
                self.serve_client(conn)
            except (OSError, ValueError):
                pass
            conn.close()

    def serve_client(self, conn):
        conn.settimeout(5)
        rfile = conn.makefile("rb")
        method, path = self.parse_request(rfile)
        headers = self.parse_headers(rfile)
        length = int(headers.get("content-length", 0))
        body = rfile.read(length).decode()
        print(method, path)
        self.handle_request(conn, method, path, body)

    def parse_request(self, rfile):
        line = rfile.readline().decode()
        method, path, version = line.split()
        return method, path

    def parse_headers(self, rfile):
        headers = {}
        while True:
            line = rfile.readline().decode().strip()
            if not line:
                break
            name, value = line.split(":", 1)
            headers[name.lower()] = value.strip()
        return headers

    def handle_request(self, conn, method, path, body):
        if path != "/":
            self.send_response(conn, 404, "Not Found", "<h1>404 Not Found</h1>")
        elif method == "GET":
            self.send_response(conn, 200, "OK", self.render_page())
        elif method == "POST":
            form = parse_qs(body)
            discipline = form.get("discipline", [""])[0].strip()
            grade = form.get("grade", [""])[0]
            if not discipline or grade not in ("1", "2", "3", "4", "5"):
                self.send_response(conn, 400, "Bad Request", "<h1>400 Bad Request</h1>")
                return
            if discipline not in self.grades:
                self.grades[discipline] = []
            self.grades[discipline].append(int(grade))
            self.send_response(conn, 200, "OK", self.render_page())
        else:
            self.send_response(conn, 405, "Method Not Allowed", "<h1>405 Method Not Allowed</h1>")

    def send_response(self, conn, status, reason, body):
        body = body.encode()
        headers = (
            f"HTTP/1.1 {status} {reason}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        conn.sendall(headers.encode() + body)

    def render_page(self):
        rows = ""
        for discipline, grades in self.grades.items():
            marks = ", ".join(map(str, grades))
            rows += f"<tr><td>{html.escape(discipline)}</td><td>{marks}</td></tr>"
        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    <form method="POST" action="/">
        <input name="discipline" placeholder="Дисциплина" required>
        <input name="grade" type="number" min="1" max="5" placeholder="Оценка" required>
        <button type="submit">Добавить</button>
    </form>
    <table border="1" cellpadding="6">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
</body>
</html>"""


if __name__ == "__main__":
    MyHTTPServer(HOST, PORT).serve_forever()

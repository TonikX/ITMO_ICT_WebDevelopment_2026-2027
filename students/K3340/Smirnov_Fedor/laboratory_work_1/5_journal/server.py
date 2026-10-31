import socket
from urllib.parse import parse_qs


class MyHTTPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.grades = {}

    def serve_forever(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Сервер запущен: http://{self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            self.serve_client(client_socket)

    def serve_client(self, client_socket):
        rfile = client_socket.makefile("rb")
        try:
            method, path, version = self.parse_request(rfile)
            headers = self.parse_headers(rfile)

            content_length = int(headers.get("Content-Length", 0))
            body = rfile.read(content_length).decode()

            print(f"Запрос: {method} {path}")
            self.handle_request(client_socket, method, path, body)
        except Exception as error:
            print(f"Не удалось обработать запрос: {error}")
        finally:
            rfile.close()
            client_socket.close()

    def parse_request(self, rfile):
        request_line = rfile.readline().decode().strip()
        parts = request_line.split()
        if len(parts) != 3:
            raise ValueError("некорректная строка запроса")
        method, path, version = parts
        return method, path, version

    def parse_headers(self, rfile):
        headers = {}
        while True:
            line = rfile.readline().decode().strip()
            if not line:
                break
            name, value = line.split(":", 1)
            headers[name.strip()] = value.strip()
        return headers

    def handle_request(self, client_socket, method, path, body):
        if method == "GET" and path == "/":
            self.send_response(client_socket, "200 OK", self.render_page())

        elif method == "POST" and path == "/":
            params = parse_qs(body)
            discipline = params.get("discipline", [""])[0].strip()
            grade = params.get("grade", [""])[0]

            if not discipline or grade not in ("2", "3", "4", "5"):
                self.send_response(
                    client_socket,
                    "400 Bad Request",
                    "<h1>400 Bad Request</h1><p>Нужны дисциплина и оценка от 2 до 5</p>",
                )
                return

            if discipline not in self.grades:
                self.grades[discipline] = []
            self.grades[discipline].append(int(grade))
            print(f"Добавлена оценка: {discipline} - {grade}")

            self.send_response(client_socket, "303 See Other", "", location="/")

        else:
            self.send_response(client_socket, "404 Not Found", "<h1>404 Not Found</h1>")

    def send_response(self, client_socket, status, body, location=None):
        body_bytes = body.encode()

        response = f"HTTP/1.1 {status}\r\n"
        response += "Content-Type: text/html; charset=utf-8\r\n"
        response += f"Content-Length: {len(body_bytes)}\r\n"
        response += "Connection: close\r\n"
        if location:
            response += f"Location: {location}\r\n"
        response += "\r\n"

        client_socket.sendall(response.encode() + body_bytes)

    def render_page(self):
        rows = ""
        for discipline, grades in self.grades.items():
            grades_text = ", ".join(str(grade) for grade in grades)
            rows += f"<tr><td>{discipline}</td><td>{grades_text}</td></tr>\n"

        if not rows:
            rows = '<tr><td colspan="2">Оценок пока нет</td></tr>'

        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>

    <form method="POST" action="/">
        <label>Дисциплина: <input type="text" name="discipline" required></label>
        <label>Оценка:
            <select name="grade">
                <option>5</option>
                <option>4</option>
                <option>3</option>
                <option>2</option>
            </select>
        </label>
        <button type="submit">Добавить</button>
    </form>

    <table border="1" cellpadding="6">
        <tr><th>Дисциплина</th><th>Оценки</th></tr>
        {rows}
    </table>
</body>
</html>"""


if __name__ == "__main__":
    server = MyHTTPServer("localhost", 8081)
    server.serve_forever()

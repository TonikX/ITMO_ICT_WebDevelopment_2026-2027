import socket
from urllib.parse import urlparse, parse_qs


class MyHTTPServer:

    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name
        self.grades = {}

    def serve_forever(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"{self.name} запущен на http://{self.host}:{self.port}", flush=True)

        while True:
            client_connection, client_address = server_socket.accept()
            print(f"подключение от {client_address}", flush=True)

            try:
                self.serve_client(client_connection)
            except Exception as e:
                print(f"ошибка: {type(e).__name__}: {e}", flush=True)
            finally:
                client_connection.close()

    def serve_client(self, connection):
        file = connection.makefile("r", encoding="utf-8")

        request_line = file.readline().strip()
        if not request_line:
            return

        method, path, params, headers, body = self.parse_request(file, request_line)
        status, response_body = self.handle_request(method, body)
        self.send_response(connection, status, response_body)

    def parse_request(self, file, request_line):
        method, url, version = request_line.split()

        parsed = urlparse(url)
        path = parsed.path
        params = parse_qs(parsed.query)

        headers = self.parse_headers(file)

        body = ""
        if "Content-Length" in headers:
            length = int(headers["Content-Length"])
            body = file.read(length)

        return method, path, params, headers, body

    def parse_headers(self, file):
        headers = {}

        while True:
            line = file.readline().strip()
            if not line:
                break
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

        return headers

    def handle_request(self, method, body):
        if method == "GET":
            return self.handle_get()
        elif method == "POST":
            return self.handle_post(body)
        else:
            return 405, self.render_error(405, "Method Not Allowed")

    def handle_get(self):
        html = self.render_page()
        return 200, html

    def handle_post(self, body):
        data = parse_qs(body)
        subject = data.get("subject", [""])[0].strip()
        grade_str = data.get("grade", [""])[0].strip()

        if subject and grade_str:
            self.grades.setdefault(subject, []).append(int(grade_str))
            print(f"добавлено: {subject} = {grade_str}", flush=True)

        html = self.render_page()
        return 200, html

    def render_page(self):
        if not self.grades:
            rows = "<tr><td colspan='2' class='empty'>Оценок нет</td></tr>"
        else:
            rows = ""
            for subject, grades in self.grades.items():
                grades_str = ", ".join(map(str, grades))
                rows += f"<tr><td>{subject}</td><td>{grades_str}</td></tr>"

        with open("index.html", "r", encoding="utf-8") as file:
            html = file.read()

        return html.replace("{%ROWS%}", rows)

    def render_error(self, status, message):
        return f"<html><body><h1>{status} {message}</h1></body></html>"

    def send_response(self, connection, status, body):
        body_bytes = body.encode("utf-8")
        reason = {200: "OK", 404: "Not Found", 405: "Method Not Allowed"}.get(status, "OK")

        response = (
            f"HTTP/1.1 {status} {reason}\r\n"
            f"Server: {self.name}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        connection.sendall(response.encode("utf-8") + body_bytes)


if __name__ == "__main__":
    host = "localhost"
    port = 8082
    name = "MyHTTPServer"
    server = MyHTTPServer(host, port, name)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
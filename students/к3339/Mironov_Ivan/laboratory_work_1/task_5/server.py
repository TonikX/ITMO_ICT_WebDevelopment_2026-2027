import socket
from urllib.parse import parse_qs


class MyHTTPServer:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.grades = {}

    def serve_forever(self):
        self.server.bind((self.host, self.port))
        self.server.listen()

        print(f"Сервер запущен: http://{self.host}:{self.port}")

        while True:
            client, address = self.server.accept()
            self.serve_client(client)

    def serve_client(self, client):
        request = self.parse_request(client)

        if request:
            self.handle_request(client, request)

        client.close()

    def parse_request(self, client):
        data = b""

        while b"\r\n\r\n" not in data:
            data += client.recv(4096)

        headers_data, body_data = data.split(b"\r\n\r\n", 1)
        lines = headers_data.decode("utf-8").split("\r\n")

        method, url, version = lines[0].split(" ")

        if "?" in url:
            path, query = url.split("?", 1)
            params = parse_qs(query)
        else:
            path = url
            params = {}

        headers = self.parse_headers(lines)

        length = int(headers.get("Content-Length", 0))

        while len(body_data) < length:
            body_data += client.recv(4096)

        body = body_data[:length].decode("utf-8")

        return {
            "method": method,
            "path": path,
            "params": params,
            "body": body
        }

    def parse_headers(self, lines):
        headers = {}

        for line in lines[1:]:
            if not line:
                break

            name, value = line.split(":", 1)
            headers[name.strip()] = value.strip()

        return headers

    def handle_request(self, client, request):
        if request["method"] == "GET":
            self.send_page(client)

        elif request["method"] == "POST":
            data = parse_qs(request["body"])

            subject = data["subject"][0]
            grade = data["grade"][0]

            if subject not in self.grades:
                self.grades[subject] = []

            self.grades[subject].append(grade)

            response = (
                "HTTP/1.1 302 Found\r\n"
                "Location: /\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client.sendall(response.encode("utf-8"))

    def send_page(self, client):
        with open("index.html", "r", encoding="utf-8") as file:
            html = file.read()

        grades_html = ""

        for subject, grades in self.grades.items():
            grades_html += f"<h3>{subject}</h3><ul>"

            for grade in grades:
                grades_html += f"<li>{grade}</li>"

            grades_html += "</ul>"

        if not grades_html:
            grades_html = "<p>Оценок пока нет.</p>"

        html = html.replace("{{GRADES}}", grades_html)

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(html.encode('utf-8'))}\r\n"
            "Connection: close\r\n"
            "\r\n"
            + html
        )

        client.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    server = MyHTTPServer(
        "127.0.0.1",
        8080,
        "GradeServer"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
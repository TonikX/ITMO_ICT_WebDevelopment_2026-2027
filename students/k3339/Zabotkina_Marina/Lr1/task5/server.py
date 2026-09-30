import socket
import sys
from urllib.parse import unquote


class MyHTTPServer:

    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name
        self.grades = []

    def serve_forever(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f"[{self.name}] Сервер запущен на http://{self.host}:{self.port}")

        while True:
            conn, _ = server_socket.accept()
            self.serve_client(conn)

    def serve_client(self, conn):
        rfile = conn.makefile("r", encoding="utf-8")

        method, url = self.parse_request(rfile)
        if not method:
            conn.close()
            return

        headers = self.parse_headers(rfile)

        body = ""
        if method == "POST":
            content_length = int(headers.get("Content-Length", 0))
            if content_length > 0:
                body = rfile.read(content_length)

        status_code, reason, response_body = self.handle_request(
            method, url, body
        )
        self.send_response(conn, status_code, reason, response_body)
        conn.close()

    def parse_request(self, rfile):
        line = rfile.readline()
        if not line:
            return None, None

        words = line.split()
        return words[0], words[1]

    def parse_headers(self, rfile):
        headers = {}
        while True:
            line = rfile.readline()
            if line in ("\r\n", "\n", ""):
                break
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
        return headers

    def handle_request(self, method, url, body):
        if method == "POST":
            subject, grade = "", ""
            pairs = body.split("&")
            for pair in pairs:
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    if k == "subject":
                        # Раскодируем русские буквы
                        subject = unquote(v.replace("+", " "))
                    elif k == "grade":
                        grade = v

            if subject and grade:
                self.grades.append({"subject": subject, "grade": grade})
                print(f"[POST] {subject} -> {grade}")

        rows = ""
        for item in self.grades:
            rows += f"<tr><td>{item['subject']}</td><td>{item['grade']}</td></tr>"

        if not rows:
            rows = "<tr><td colspan='2'>Записей пока нет</td></tr>"

        with open("grade.html", "r", encoding="utf-8") as f:
            template = f.read()

        html_body = template.replace("{{ grades_table }}", rows)
        return 200, "OK", html_body

    def send_response(self, conn, status_code, reason, body):
        status_line = f"HTTP/1.1 {status_code} {reason}\r\n"
        headers = (
            f"Content-Type: text/html; charset=UTF-8\r\n"
            f"Content-Length: {len(body.encode('utf-8'))}\r\n"
            f"Connection: close\r\n"
        )
        conn.sendall(status_line.encode("utf-8"))
        conn.sendall(headers.encode("utf-8"))
        conn.sendall(b"\r\n")
        conn.sendall(body.encode("utf-8"))


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8085
    name = sys.argv[3] if len(sys.argv) > 3 else "MyHTTPServer"

    serv = MyHTTPServer(host, port, name)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
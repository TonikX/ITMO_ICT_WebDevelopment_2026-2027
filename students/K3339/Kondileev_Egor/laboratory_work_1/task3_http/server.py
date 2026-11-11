"""Задание 3: минимальный HTTP-сервер на socket, отдающий index.html."""
from pathlib import Path
import socket

HOST = "127.0.0.1"
PORT = 8080
HTML_FILE = Path(__file__).with_name("index.html")

def make_response(status, content_type, body):
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii")
    return headers + body

def main():
    if not HTML_FILE.exists():
        raise FileNotFoundError(f"Не найден файл страницы: {HTML_FILE}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"HTTP-сервер запущен: http://{HOST}:{PORT}/")
        print(f"HTML берётся из файла: {HTML_FILE}")

        while True:
            connection, address = server.accept()
            with connection:
                request = connection.recv(4096).decode("iso-8859-1", errors="replace")
                first_line = request.splitlines()[0] if request else ""
                print(f"{address}: {first_line}")

                if first_line.startswith(("GET / ", "GET /index.html ")):
                    body = HTML_FILE.read_bytes()
                    response = make_response("200 OK", "text/html; charset=utf-8", body)
                else:
                    body = b"<h1>404 Not Found</h1>"
                    response = make_response("404 Not Found", "text/html; charset=utf-8", body)

                connection.sendall(response)

if __name__ == "__main__":
    main()

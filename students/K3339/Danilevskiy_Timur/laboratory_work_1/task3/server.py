"""Задание 3. HTTP-сервер на сокетах, отдающий страницу из index.html."""
import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096
INDEX_FILE = Path(__file__).with_name("index.html")


def build_response(status, content_type, body):
    # HTTP-ответ: стартовая строка, заголовки, пустая строка, тело.
    # Строки разделяются \r\n, Content-Length считается в байтах
    head = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return head.encode("utf-8") + body


def handle_request(request):
    request_line = request.split("\r\n", 1)[0]
    parts = request_line.split()
    path = parts[1] if len(parts) == 3 else ""

    if path in ("/", "/index.html"):
        return build_response("200 OK", "text/html; charset=utf-8", INDEX_FILE.read_bytes())
    return build_response("404 Not Found", "text/plain; charset=utf-8", "Страница не найдена".encode("utf-8"))


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"HTTP-сервер запущен: http://{HOST}:{PORT}/")

        while True:
            conn, addr = server.accept()
            with conn:
                request = conn.recv(BUFFER_SIZE).decode("iso-8859-1")
                if not request:
                    continue
                print(f"{addr[0]}:{addr[1]} — {request.splitlines()[0]}")
                conn.sendall(handle_request(request))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен")

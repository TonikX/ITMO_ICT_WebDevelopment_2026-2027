import socket
from pathlib import Path

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8000))
server.listen(5)

print("Сервер запущен: http://127.0.0.1:8000")

html_path = Path(__file__).parent / "index.html"

while True:
    connection, address = server.accept()

    request = b""
    while b"\r\n\r\n" not in request:
        data = connection.recv(1024)
        if not data:
            break
        request += data

    if request:
        html = html_path.read_bytes()

        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(html)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        connection.sendall(headers.encode("utf-8") + html)

    connection.close()
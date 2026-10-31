import socket
from pathlib import Path

ADDRESS = ("localhost", 8080)
PAGE = Path(__file__).parent / "index.html"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(ADDRESS)
    sock.listen()
    print("HTTP-сервер запущен: http://localhost:8080")

    while True:
        conn, address = sock.accept()
        with conn:
            request = conn.recv(1024).decode()
            print(address, request.split("\r\n")[0])

            body = PAGE.read_bytes()
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            conn.sendall(headers.encode() + body)

import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8080

BASE_DIR = Path(__file__).parent
HTML_FILE = BASE_DIR / "index.html"


def create_response():
    try:
        body = HTML_FILE.read_bytes()

        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            + f"Content-Length: {len(body)}\r\n".encode("utf-8")
            + b"Connection: close\r\n"
            b"\r\n"
            + body
        )

        return response

    except FileNotFoundError:
        body = b"<h1>404 Not Found</h1>"

        return (
            b"HTTP/1.1 404 Not Found\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            + f"Content-Length: {len(body)}\r\n".encode("utf-8")
            + b"Connection: close\r\n"
            b"\r\n"
            + body
        )


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"HTTP server запущен: http://{HOST}:{PORT}")

while True:
    connection, client_address = server_socket.accept()

    print(f"Подключен клиент: {client_address}")

    try:
        request = connection.recv(4096).decode("utf-8")

        print("HTTP request:")
        print(request)

        response = create_response()

        connection.sendall(response)

    finally:
        connection.close()
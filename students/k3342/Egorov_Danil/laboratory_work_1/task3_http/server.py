import os
import socket

HOST, PORT = "localhost", 8080
INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")


def build_response(status: str, body: bytes) -> bytes:
    headers = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"HTTP-сервер запущен: http://{HOST}:{PORT}")

while True:
    conn, addr = server_socket.accept()
    request = conn.recv(4096).decode("utf-8", errors="replace")
    first_line = request.splitlines()[0] if request else "(пусто)"
    print(f"Запрос от {addr}: {first_line}")

    try:
        with open(INDEX_PATH, "rb") as f:
            response = build_response("200 OK", f.read())
    except FileNotFoundError:
        response = build_response("404 Not Found", "<h1>index.html не найден</h1>".encode("utf-8"))

    conn.sendall(response)
    conn.close()

import socket
from pathlib import Path

HOST = "localhost"
PORT = 9003
INDEX_FILE = Path(__file__).with_name("index.html")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"HTTP-сервер запущен: http://{HOST}:{PORT}/")

try:
    while True:
        client_connection, client_address = server_socket.accept()

        request = b""
        while b"\r\n\r\n" not in request:
            chunk = client_connection.recv(1024)
            if not chunk:
                break
            request += chunk

        if request:
            request_line = request.split(b"\r\n")[0].decode()
            print(f"Запрос от {client_address}: {request_line}")

            body = INDEX_FILE.read_bytes()

            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode() + body
            client_connection.sendall(http_response)

        client_connection.close()
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()

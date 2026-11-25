import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8083
INDEX = Path(__file__).parent / "index.html"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"HTTP-сервер запущен: http://{HOST}:{PORT}/")

while True:
    conn, address = server.accept()
    conn.settimeout(5)
    try:
        request = conn.recv(1024).decode()
        if request:
            print(request.split("\r\n")[0])
            body = INDEX.read_bytes()
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            conn.sendall(headers.encode() + body)
    except OSError:
        pass
    conn.close()

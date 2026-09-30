import socket
from pathlib import Path

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen(5)
print("Откройте http://127.0.0.1:8080")

while True:
    client, addr = server.accept()
    with client, client.makefile('rb') as request:
        # Читаем заголовки до пустой строки.
        line = request.readline()
        if not line:
            continue
        while line not in (b'\r\n', b''):
            line = request.readline()

        html = Path(__file__).with_name('index.html').read_bytes()
        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(html)}\r\n"
            "Connection: close\r\n\r\n"
        )
        client.sendall(headers.encode() + html)

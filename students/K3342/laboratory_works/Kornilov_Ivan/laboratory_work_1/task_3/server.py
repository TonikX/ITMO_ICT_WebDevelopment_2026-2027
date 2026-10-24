import socket
from pathlib import Path

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8080))
server_socket.listen(1)

html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
body_bytes = html.encode("utf-8")
headers = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=UTF-8\r\n"
    f"Content-Length: {len(body_bytes)}\r\n"
    "Connection: close\r\n"
    "\r\n"
)
response = headers.encode("utf-8") + body_bytes

while True:
    client_connection, _ = server_socket.accept()
    client_connection.recv(1024)
    client_connection.sendall(response)
    client_connection.close()

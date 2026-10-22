import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8080

with socket.socket() as server:
    server.bind((HOST, PORT))
    server.listen()

    while True:
        connection, address = server.accept()
        with connection:
            connection.recv(1024)
            body = Path(__file__).with_name("index.html").read_bytes()
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/html; charset=utf-8\r\n"
                + f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
                + body
            )
            connection.sendall(response)

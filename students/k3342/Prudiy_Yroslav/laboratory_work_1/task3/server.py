import socket
from pathlib import Path

HOST, PORT = "127.0.0.1", 5001
PAGE = Path(__file__).with_name("index.html")


def run_server():
    body = PAGE.read_bytes()

    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"http://{HOST}:{PORT}")

        while True:
            connection, _ = server.accept()

            with connection:
                connection.recv(1024)

                connection.sendall(headers + body)


if __name__ == "__main__":
    run_server()

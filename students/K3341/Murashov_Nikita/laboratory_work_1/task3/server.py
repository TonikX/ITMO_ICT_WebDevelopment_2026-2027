"""HTTP-сервер задания 3: отдаёт index.html из своей папки."""

import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 11003


def build(body: bytes) -> bytes:
    """Собирает HTTP-ответ 200 OK с HTML-телом.

    Args:
        body: Байты HTML-страницы.

    Returns:
        Байты полного HTTP-ответа.
    """
    head = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("utf-8")
    return head + body


def main() -> None:
    """Запускает сервер и раздаёт index.html каждому подключению.

    Args:
        None.

    Returns:
        None.
    """
    body = (Path(__file__).parent / "index.html").read_bytes()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"HTTP сервер: {HOST}:{PORT}")
        while True:
            conn, _ = sock.accept()
            with conn:
                conn.recv(4096)
                conn.sendall(build(body))


if __name__ == "__main__":
    main()

"""Задание 3. HTTP-сервер на socket: отдаёт index.html.

Ответ собирается вручную: строка статуса, заголовки, пустая строка, тело.
Проверка: запустить сервер и открыть в браузере http://127.0.0.1:8080
"""
import os
import socket

HOST, PORT = "127.0.0.1", 8080
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")


def build_response(body: bytes) -> bytes:
    headers = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/html; charset=utf-8",
        f"Content-Length: {len(body)}",          # длина тела в байтах, а не в символах
        "Connection: close",
    ]
    return ("\r\n".join(headers) + "\r\n\r\n").encode("utf-8") + body


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"Откройте http://{HOST}:{PORT}")
        while True:
            conn, _ = srv.accept()
            with conn:
                request = conn.recv(4096).decode("utf-8", errors="replace")
                if request:
                    print(request.splitlines()[0])  # например: GET / HTTP/1.1
                with open(PAGE, "rb") as f:
                    conn.sendall(build_response(f.read()))


if __name__ == "__main__":
    main()

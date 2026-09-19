from pathlib import Path
import socket

HOST = "127.0.0.1"
PORT = 8083
BUFFER_SIZE = 4096
INDEX_PATH = Path(__file__).with_name("index.html")


def build_response(body: bytes) -> bytes:
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body


def main() -> None:
    html = INDEX_PATH.read_bytes()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"HTTP-сервер: http://{HOST}:{PORT}/")
        print("Открой адрес в браузере или сделай curl.")

        while True:
            conn, address = server.accept()
            with conn:
                request = conn.recv(BUFFER_SIZE)
                print(f"Запрос от {address}:\n{request.decode('utf-8', errors='replace')}")
                conn.sendall(build_response(html))


if __name__ == "__main__":
    main()

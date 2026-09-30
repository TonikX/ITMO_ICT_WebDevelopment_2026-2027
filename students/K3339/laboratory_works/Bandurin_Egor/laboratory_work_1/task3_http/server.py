import socket
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 1024
HTML_FILE = Path(__file__).with_name("index.html")


def build_http_response() -> bytes:
    body = HTML_FILE.read_bytes()
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body


def main() -> None:
    response = build_http_response()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"HTTP server is running at http://{HOST}:{PORT}")

        try:
            while True:
                connection, client_address = server_socket.accept()
                with connection:
                    request = connection.recv(BUFFER_SIZE).decode(
                        "utf-8", errors="replace"
                    )
                    if request:
                        request_line = request.splitlines()[0]
                        print(f"{client_address}: {request_line}")
                        connection.sendall(response)
        except KeyboardInterrupt:
            print("\nHTTP server stopped")


if __name__ == "__main__":
    main()

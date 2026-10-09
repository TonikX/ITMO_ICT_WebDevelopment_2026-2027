import socket


HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"HTTP-сервер запущен на {HOST}:{PORT}")
        print("Откройте в браузере: http://127.0.0.1:8080")
        print("Ожидание HTTP-запросов...")

        while True:
            client_socket, client_address = server_socket.accept()

            with client_socket:
                request = client_socket.recv(BUFFER_SIZE).decode(
                    "utf-8",
                    errors="ignore",
                )

                if not request:
                    continue

                request_line = request.splitlines()[0]

                print(f"\nПодключён клиент: {client_address}")
                print(f"Получен запрос: {request_line}")

                try:
                    with open("index.html", "rb") as html_file:
                        body = html_file.read()

                    headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html; charset=utf-8\r\n"
                        f"Content-Length: {len(body)}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                    ).encode("utf-8")

                    client_socket.sendall(headers + body)

                    print("HTML-страница отправлена клиенту")
                except FileNotFoundError:
                    body = "Файл index.html не найден".encode("utf-8")

                    headers = (
                        "HTTP/1.1 500 Internal Server Error\r\n"
                        "Content-Type: text/plain; charset=utf-8\r\n"
                        f"Content-Length: {len(body)}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                    ).encode("utf-8")

                    client_socket.sendall(headers + body)

                    print("Ошибка: файл index.html не найден")


if __name__ == "__main__":
    main()
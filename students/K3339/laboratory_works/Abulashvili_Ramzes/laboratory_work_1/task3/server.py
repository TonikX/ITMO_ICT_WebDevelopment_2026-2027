import socket
from pathlib import Path


PORT = 8080


def main():
    body = Path(__file__).with_name("index.html").read_bytes()
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", PORT))
        server.listen(5)
        print(f"HTTP-сервер запущен: http://127.0.0.1:{PORT}")
        while True:
            client, address = server.accept()
            with client:
                client.settimeout(5)
                try:
                    request = b""
                    while b"\r\n\r\n" not in request:
                        part = client.recv(1024)
                        if not part:
                            break
                        request += part
                    if b"\r\n\r\n" in request:
                        print(request.split(b"\r\n", 1)[0].decode("iso-8859-1"))
                        client.sendall(headers.encode("ascii") + body)
                except socket.timeout:
                    print("Время ожидания запроса истекло.")
                except OSError as error:
                    print(f"Ошибка соединения: {error}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    except OSError as error:
        print(f"Ошибка сети: {error}")

import os
import select
import socket


def run_server():
    HOST, PORT = '127.0.0.1', 9000
    path = 'index.html'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    try:
        while True:
            readable, _, _ = select.select([sock], [], [], 0.5)
            if sock in readable:
                client_sock, client_addr = sock.accept()
                print(f"Подключился {client_addr}")

                try:
                    request = client_sock.recv(1024)
                    print(request.decode("utf-8"))

                    if os.path.exists(path):
                        with open(path, 'rb') as f:
                            html_content = f.read()

                        content_len = len(html_content)

                        headers = (
                            "HTTP/1.1 200OK\r\n"
                            "Content-Type: text/html; charset=utf-8\r\n"
                            f"Content-Length: {content_len}\r\n"
                            "Connection: close\r\n\r\n"
                        )
                        response = headers.encode("utf-8") + html_content
                    else:
                        error_body = "<h1>404 Not Found</h1>".encode('utf-8')
                        headers = (
                            "HTTP/1.1 404 Not Found\r\n"
                            "Content-Type: text/html; charset=utf-9\r\n"
                            f"Content-Length: {len(error_body)}\r\n"
                            "Connection: close\r\n\r\n"
                        )
                        response = headers.encode("utf-8") + error_body

                    client_sock.sendall(response)
                except Exception as e:
                    print(f"Ошибка при обработке запроса: {e}")
                finally:
                    client_sock.close()
    except KeyboardInterrupt:
        print("\n[OK] Сервер успешно остановлен (Ctrl+C).")
    finally:
        sock.close()


if __name__ == "__main__":
    run_server()


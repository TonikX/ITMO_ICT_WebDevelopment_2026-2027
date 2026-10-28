import socket
import os

HOST = '127.0.0.1'
PORT = 9092

def build_http_response(
        body: bytes,
        content_type: str = 'text/html; charset=utf-8',
        status: str = '200 OK'
) -> bytes:
    headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return headers.encode('utf-8') + body

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[Сервер] Запущен на http://{HOST}:{PORT}")

    index_path = os.path.join(os.path.dirname(__file__), 'index.html')

    while True:
        conn, addr = server_socket.accept()
        print(f"[Сервер] Подключение от {addr}")
        try:
            # Читаем запрос
            request = conn.recv(4096).decode('utf-8', errors='ignore')
            first_line = request.split('\r\n')[0]
            print(f"[Сервер] Запрос: {first_line}")

            # Отдаём index.html на любой GET-запрос
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    body = f.read()
                response = build_http_response(body)
            else:
                body = b"<h2>index.html not Found</h2>"
                response = build_http_response(body, status='404 Not Found')

            conn.sendall(response)
        except Exception as e:
            print(f"[Сервер] Ошибка: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    main()
import socket
import os

HOST = '127.0.0.1'
PORT = 8082

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'index.html')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[HTTP Server] Запущен на http://{HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        with conn:
            print(f"[HTTP Server] Подключение от {addr}")

            request = conn.recv(1024).decode('utf-8')
            print(f"[HTTP Server] Запрос:\n{request}")

            try:
                with open(HTML_FILE, 'r', encoding='utf-8') as f:
                    body = f.read()

                response_headers = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )

                conn.sendall(response_headers.encode('utf-8') + body.encode('utf-8'))
                print("[HTTP Server] Файл успешно отправлен.")

            except FileNotFoundError:
                error_body = "<h1>404 Not Found</h1>"
                response = f"HTTP/1.1 404 Not Found\r\nContent-Length: {len(error_body)}\r\n\r\n{error_body}"
                conn.sendall(response.encode('utf-8'))

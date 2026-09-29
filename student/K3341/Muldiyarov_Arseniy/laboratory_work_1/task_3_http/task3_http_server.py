import socket
import os

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8082))
server_socket.listen(1)
print("HTTP сервер запущен на http://localhost:8082")

while True:
    conn, addr = server_socket.accept()
    try:
        # Читаем запрос
        request = conn.recv(1024)

        # Читаем файл
        file_path = 'index.html'
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                body = f.read()

            # Формируем HTTP заголовки
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            conn.sendall(headers.encode('utf-8') + body)
        else:
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\nFile not found")
    finally:
        conn.close()
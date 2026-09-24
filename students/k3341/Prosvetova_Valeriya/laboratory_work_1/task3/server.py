import socket
import os

HOST = 'localhost'
PORT = 9003
HTML_FILE = os.path.join(os.path.dirname(__file__), 'index.html')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"HTTP-сервер запущен на {HOST}:{PORT}...")

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html_content = f.read()

while True:
    conn, addr = server_socket.accept()
    print(f"Подключение от {addr}")

    request = conn.recv(1024).decode(errors='ignore')
    print(f"Запрос клиента:\n{request.splitlines()[0] if request else ''}")

    body = html_content.encode('utf-8')
    http_response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode('utf-8') + body

    conn.sendall(http_response)
    conn.close()

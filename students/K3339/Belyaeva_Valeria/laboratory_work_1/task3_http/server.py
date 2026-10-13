import os
import socket

# index.html лежит рядом со скриптом - так сервер работает из любой папки
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Позволяет сразу перезапускать сервер на том же порту
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 8083))
server_socket.listen(1)
print("HTTP сервер запущен на http://127.0.0.1:8083")

while True:
    conn, addr = server_socket.accept()
    request = conn.recv(1024)

    try:
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            html = f.read()
        status = "200 OK"
    except FileNotFoundError:
        html = "<h1>Error 404: index.html not found</h1>"
        status = "404 Not Found"

    # Формируем HTTP-ответ
    response = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html.encode('utf-8'))}\r\n"
        "Connection: close\r\n\r\n"
        f"{html}"
    )

    conn.sendall(response.encode('utf-8'))
    conn.close()

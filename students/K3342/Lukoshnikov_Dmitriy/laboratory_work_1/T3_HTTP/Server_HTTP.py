import socket

HOST = 'localhost'
PORT = 8082

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"HTTP сервер запущен на {HOST}:{PORT}...")

with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()
html_bytes = html_content.encode('utf-8')

print(f"Ссылка для подключения - http://localhost:8082/")

while True:
    connection, address = server_socket.accept()
    print(f'Подключение от {address}')
    request = connection.recv(1024).decode('utf-8', errors='ignore')
    print(f'Запрос клиента:\n{request}')
    header = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    http_response = header.encode('utf-8') + html_bytes
    connection.sendall(http_response)
    connection.close()
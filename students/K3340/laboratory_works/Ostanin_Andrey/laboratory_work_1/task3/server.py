import socket
from pathlib import Path

HOST = 'localhost'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))  

server_socket.listen(5)
print(f"HTTP сервер запущен на {HOST}:{PORT}...")

html_bytes = Path(__file__).parent.joinpath('index.html').read_bytes()

while True:
    client_connection, client_address = server_socket.accept()
    print(f'Подключение от {client_address}')

    request = client_connection.recv(2048).decode()
    print(f'Запрос клиента:\n{request}')

    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode('utf-8')

    client_connection.sendall(headers + html_bytes)
    client_connection.close()
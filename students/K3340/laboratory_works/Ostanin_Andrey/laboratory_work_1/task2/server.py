# Теорема Пифагора

import socket
import math

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8080))
server_socket.listen(1)
print("Сервер запущен и ожидает...")

while True:
    client_connection, client_address = server_socket.accept()
    print(f"Подключение от {client_address}")

    request = client_connection.recv(1024).decode()
    print(f"Запрос от клиента: {request}")

    a, b = map(int, request.split())
    c = math.sqrt(a**2 + b**2)

    client_connection.sendall(str(c).encode())
    client_connection.close()
import socket
import math

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(("localhost", 8080))
server_socket.listen(1)

print("Сервер запущен на порту 8080...")

while True:
    client_connection, client_address = server_socket.accept()
    print(f'Подключение от {client_address}')

    request = client_connection.recv(1024).decode()
    a, b, c = map(float, request.split())
    d = b * b - 4 * a * c
    x1 = (-b + math.sqrt(d)) / (2 * a)
    x2 = (-b - math.sqrt(d)) / (2 * a)

    print(f'корни уравнения будут {x1} и {x2}')
    response = f'корни уравнения будут {x1} и {x2}'
    client_connection.sendall(response.encode())

    client_connection.close()
import math
import socket

HOST = "localhost"
PORT = 9002

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"TCP-сервер запущен на {HOST}:{PORT}")

try:
    while True:
        client_connection, client_address = server_socket.accept()
        print(f"Подключение от {client_address}")

        request = client_connection.recv(1024).decode()
        print(f"Запрос от клиента: {request}")

        try:
            a, b = map(float, request.split())
            if a <= 0 or b <= 0:
                raise ValueError
            response = f"Гипотенуза c = {math.hypot(a, b)}"
        except ValueError:
            response = "Ошибка: нужно ввести два положительных числа - длины катетов"

        client_connection.sendall(response.encode())
        client_connection.close()
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()

import math
import socket

host = 'localhost'
port = 8081
def pifagor(k1, k2):
    return math.sqrt(k1**2 + k2**2)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((host, port))

server_socket.listen(1)
print(f"Сервер запущен на порту {port}...")

while True:
    client_connection, client_address = server_socket.accept()
    print(f'Подключение от {client_address}')

    request = client_connection.recv(1024).decode()
    print(f"Получено сообщение от клиента {client_address} - {request}")

    k1, k2 = map(float, request.split(','))
    response = f"Гипотенуза = {str(pifagor(k1, k2))}"
    client_connection.sendall(response.encode())
    print(f"Ответ отправлен клиенту {client_address} - {response}")

    client_connection.close()

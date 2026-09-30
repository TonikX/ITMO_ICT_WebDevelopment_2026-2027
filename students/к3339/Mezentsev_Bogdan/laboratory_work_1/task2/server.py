import math
import socket


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8081))
server_socket.listen(1)
print("Сервер запущен на порту 8081")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Подключение от {client_address}")

    client_data = client_socket.recv(1024).decode()
    print(f"Получены коэффициенты: {client_data}")

    a, b, c = map(float, client_data.split(","))
    discriminant = b**2 - 4 * a * c

    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        result = f"Два корня: x1 = {x1}, x2 = {x2}"
    elif discriminant == 0:
        x = -b / (2 * a)
        result = f"Один корень: x = {x}"
    else:
        result = "Действительных корней нет"

    client_socket.sendall(result.encode())
    client_socket.close()

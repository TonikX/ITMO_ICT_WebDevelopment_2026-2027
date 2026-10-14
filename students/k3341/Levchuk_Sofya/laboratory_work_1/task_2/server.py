import socket
import math

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 8081))

server_socket.listen(1)
print("сервер запущен на localhost:8081")

client_connection, client_address = server_socket.accept()
print(f"подключение от клиента: {client_address}")

request = client_connection.recv(1024).decode()
print(f"получено сообщение от клиента: {request}")

a, b, c = map(float, request.split(', '))

d = b ** 2 - 4 * a * c

if d > 0:
    x1 = (-b + math.sqrt(d)) / (2 * a)
    x2 = (-b - math.sqrt(d)) / (2 * a)
    response = f"D = {d}, корни: x1 = {x1}, x2 = {x2}"
elif d == 0:
    x = (-b) / (2 * a)
    response = f"D = {d}, корень: x = {x}"
else:
    response = f"D = {d}, корней нет"

client_connection.sendall(response.encode())

client_connection.close()
import math
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8080))
server_socket.listen(1)

while True:
    client_connection, _ = server_socket.accept()
    request = client_connection.recv(1024).decode("utf-8")
    a, b = map(float, request.split())
    hypotenuse = math.sqrt(a ** 2 + b ** 2)
    client_connection.sendall(f"Гипотенуза: {hypotenuse:.4f}".encode("utf-8"))
    client_connection.close()

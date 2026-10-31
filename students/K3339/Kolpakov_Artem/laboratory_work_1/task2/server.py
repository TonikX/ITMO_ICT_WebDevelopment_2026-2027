import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(("localhost", 8080))

server_socket.listen(1)

print("Сервер запущен")

while True:
    client_connection, client_address = server_socket.accept()
    print("Подключился клиент:", client_address)

    data = client_connection.recv(1024).decode()
    a, h = map(float, data.split())

    area = a * h

    client_connection.sendall(str(area).encode())
    client_connection.close()
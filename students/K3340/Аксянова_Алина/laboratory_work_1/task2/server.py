import socket

HOST = "localhost"
PORT = 8081

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(1)

print(f"TCP-сервер запущен на {HOST}:{PORT}")

while True:
    client_connection, client_address = server_socket.accept()
    print(f"Подключение от {client_address}")

    data = client_connection.recv(1024).decode()

    a, b, h = map(float, data.split())

    area = (a + b) * h / 2

    client_connection.sendall(str(area).encode())

    client_connection.close()
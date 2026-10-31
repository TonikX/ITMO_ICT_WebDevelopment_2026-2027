import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("localhost", 8080))

print("Сервер запущен...")

while True:
    message, client_address = server_socket.recvfrom(1024)
    print("Сообщение от клиента:", message.decode())

    server_socket.sendto(
        "Hello, client".encode(),
        client_address
    )
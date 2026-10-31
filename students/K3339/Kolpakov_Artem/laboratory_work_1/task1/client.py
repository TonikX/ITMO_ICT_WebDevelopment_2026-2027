import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto(
    "Hello, server".encode(),
    ("localhost", 8080)
)

message, server_address = client_socket.recvfrom(1024)
print("Сообщение от сервера:", message.decode())

client_socket.close()
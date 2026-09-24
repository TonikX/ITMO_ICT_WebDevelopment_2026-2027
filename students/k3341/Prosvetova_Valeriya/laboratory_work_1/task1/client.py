import socket

HOST = 'localhost'
PORT = 9001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "Hello, server"
client_socket.sendto(message.encode(), (HOST, PORT))
print(f"Отправлено серверу: {message}")

data, server_address = client_socket.recvfrom(1024)
print(f"Получено от сервера: {data.decode()}")

client_socket.close()

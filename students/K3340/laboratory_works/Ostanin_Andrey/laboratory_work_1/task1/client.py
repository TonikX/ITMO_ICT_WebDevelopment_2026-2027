import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 8080)

message = "Hello, server"
client_socket.sendto(message.encode('utf-8'), server_address)
print(f"Отправлено серверу: {message}")

data, server = client_socket.recvfrom(1024)
response = data.decode('utf-8')
print(f"Получено от сервера: {response}")

client_socket.close()
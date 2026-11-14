import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('127.0.0.1', 9090)
client_socket.sendto(b"Hello, server", server_address)

data, server_address = client_socket.recvfrom(1024)

print("Получено от сервера:", data.decode('utf-8'))

client_socket.close()
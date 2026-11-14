import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind(('127.0.0.1', 9090))
print("Сервер запущен")

data, client_address = server_socket.recvfrom(1024)

print("Получено от клиента:", data.decode('utf-8'))

server_socket.sendto(b"Hello, client", client_address)

server_socket.close()
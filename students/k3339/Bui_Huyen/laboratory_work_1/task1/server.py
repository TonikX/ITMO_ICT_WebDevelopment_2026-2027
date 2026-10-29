import socket

HOST = "127.0.0.1"
PORT = 5000

# UDP сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Привязываем сокет к адресу и порту
server_socket.bind((HOST, PORT))

print("Server is waiting for a message...")

# Получаем данные
data, client_address = server_socket.recvfrom(1024)
message = data.decode()
print('Client:', message)

# Ответим клиенту.
response = "Hello, client!"
server_socket.sendto(response.encode(), client_address)
server_socket.close()
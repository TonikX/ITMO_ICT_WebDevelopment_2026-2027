import socket

HOST = '127.0.0.1'
PORT = 5000

# UDP сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = 'Hello, server!'

client_socket.sendto(message.encode(), (HOST, PORT))

# Получаем результат от сервера
data, server_address = client_socket.recvfrom(1024)
response = data.decode()
print("Server:", response)

client_socket.close()
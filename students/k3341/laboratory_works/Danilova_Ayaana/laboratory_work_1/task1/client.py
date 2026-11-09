import socket

# Создаем UDP-сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 12345)
message = "Привет, UDP сервер!".encode('utf-8')

# Отправляем «открытку» напрямую на адрес сервера без предварительного звонка
client_socket.sendto(message, server_address)

# Ждем ответа
data, _ = client_socket.recvfrom(1024)
print(f"Ответ от сервера: {data.decode('utf-8')}")

client_socket.close()
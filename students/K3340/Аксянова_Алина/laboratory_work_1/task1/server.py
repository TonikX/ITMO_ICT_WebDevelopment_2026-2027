import socket

HOST = "localhost"
PORT = 8080

# создаем сокет по протоколу UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# привязываем сокет к адресу и порту
server_socket.bind((HOST, PORT))

print(f"UDP-сервер запущен на {HOST}:{PORT}")

# получаем сообщение от клиента
data, client_address = server_socket.recvfrom(1024)

message = data.decode()
print(f"Сообщение от клиента: {message}")

# отправляем ответ клиенту
response = "Hello, client"
server_socket.sendto(response.encode(), client_address)

# Закрываем соединение
server_socket.close()
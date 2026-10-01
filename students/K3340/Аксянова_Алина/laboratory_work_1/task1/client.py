import socket

HOST = "localhost"
PORT = 8080

# создаем сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# отправляем сообщение серверу
message = "Hello, server"
client_socket.sendto(message.encode(), (HOST, PORT))

# ответ от сервера
data, server_address = client_socket.recvfrom(1024)

# декодируем и выводим полученное сообщение
response = data.decode()
print(f"Ответ от сервера: {response}")

# закрываем сокет
client_socket.close()
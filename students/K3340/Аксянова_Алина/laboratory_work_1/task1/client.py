import socket

HOST = "localhost"
PORT = 8080

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "Hello, server"
client_socket.sendto(message.encode(), (HOST, PORT))

data, server_address = client_socket.recvfrom(1024)

response = data.decode()
print(f"Ответ от сервера: {response}")

client_socket.close()
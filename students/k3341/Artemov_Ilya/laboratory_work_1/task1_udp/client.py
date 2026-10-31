import socket

HOST = "localhost"
PORT = 9001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto("Hello, server".encode(), (HOST, PORT))

data, server_address = client_socket.recvfrom(1024)
print(f"Сообщение от сервера: {data.decode()}")

client_socket.close()

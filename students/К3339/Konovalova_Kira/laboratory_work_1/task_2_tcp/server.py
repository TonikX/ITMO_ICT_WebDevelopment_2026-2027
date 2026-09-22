import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("127.0.0.1", 5002)
server_socket.bind(server_address)
server_socket.listen()

client_socket, client_address = server_socket.accept() #ждем клиента

data = client_socket.recv(1024) #используется recv так как клиент уже подключен
message = data.decode()

base, height = message.split()
base = float(base)
height = float(height)
area = base * height
print("Received base:", base)
print("Received height:", height)
print("Calculated area:", area)

client_socket.send(str(area).encode())

client_socket.close()
server_socket.close()
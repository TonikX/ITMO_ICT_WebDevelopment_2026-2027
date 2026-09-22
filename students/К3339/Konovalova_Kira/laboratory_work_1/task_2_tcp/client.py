import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("127.0.0.1", 5002)
client_socket.connect(server_address)

base = input("Enter base: ")
height = input("Enter height: ")
message = base + " " + height

client_socket.send(message.encode())

data = client_socket.recv(1024)
print("Area:", data.decode())

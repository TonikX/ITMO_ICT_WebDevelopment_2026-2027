import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ("127.0.0.1", 5001)

message = "Hello, server"

client_socket.sendto(message.encode(), server_address)

data, server_address = client_socket.recvfrom(1024)

response = data.decode()
print(response)
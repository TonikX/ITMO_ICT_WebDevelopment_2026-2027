import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("127.0.0.1", 5001)

server_socket.bind(server_address)

data, client_address = server_socket.recvfrom(1024) 

message = data.decode()
print(message)

response = "Hello, client"
server_socket.sendto(response.encode(), client_address)
server_socket.close()
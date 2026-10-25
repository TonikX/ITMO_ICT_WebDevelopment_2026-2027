import socket

HOST = "127.0.0.1"
PORT = 8080
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

data, client_address = server_socket.recvfrom(1024)
message = data.decode()
print(message)

encode_message = "Hello, client".encode()
server_socket.sendto(encode_message, client_address)

server_socket.close()

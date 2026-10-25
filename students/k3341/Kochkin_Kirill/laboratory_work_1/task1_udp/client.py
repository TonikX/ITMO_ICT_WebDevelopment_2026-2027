import socket

HOST = "127.0.0.1"
PORT = 8080
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (HOST, PORT)

encode_message = 'Hello server'.encode()
client_socket.sendto(encode_message, server_address)

data, server_address = client_socket.recvfrom(1024)
message = data.decode()
print(message)

client_socket.close()
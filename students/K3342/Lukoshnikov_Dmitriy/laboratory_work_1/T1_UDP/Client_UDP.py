import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto(b'Hello, server', ('localhost', 8080))

data, adr = client_socket.recvfrom(1024)
print(data.decode())

client_socket.close()
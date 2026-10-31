import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 8080))

data, adr = server_socket.recvfrom(1024)
print(data.decode())

server_socket.sendto(b'Hello, client', adr)

server_socket.close()
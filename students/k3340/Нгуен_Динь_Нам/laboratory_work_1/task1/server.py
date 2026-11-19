import socket

socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_server.bind(('localhost', 8080))

request, address = socket_server.recvfrom(1024)

print(request.decode('utf-8'))

response = b'Hello, client'
socket_server.sendto(response, address)

socket_server.close()
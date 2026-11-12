import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto(b'Hello, server', ('localhost', 8080))

response, address = client_socket.recvfrom(1024)

print(response.decode('utf-8'))

client_socket.close()




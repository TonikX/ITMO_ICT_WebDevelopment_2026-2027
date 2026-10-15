import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(('localhost', 30000))

print('Server started at port 30000')
while True:
    data, address = server.recvfrom(1024)
    print(data)
    server.sendto(b'Hello, client', address)

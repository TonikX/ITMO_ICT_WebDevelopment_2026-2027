import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("127.0.0.1", 9090))

while True:
    message, address = server.recvfrom(1024)
    print(message.decode())
    server.sendto(b"Hello, client", address)

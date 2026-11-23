import socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("0.0.0.0", 8080))

while True:
    data, adres = server.recvfrom(1024)
    print(data.decode())
    response = "Hello, client".encode()
    server.sendto(response, adres)


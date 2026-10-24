import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("localhost", 8080))

while True:
    data, client_address = server_socket.recvfrom(1024)
    print(data.decode("utf-8"))
    server_socket.sendto("Hello, client".encode("utf-8"), client_address)

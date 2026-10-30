import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 9090)
message = "Hello, Server"

sock.sendto(message.encode('utf-8'), server_address)

data, server_info = sock.recvfrom(1024)
sock.close()

print(f"Сообщение от сервера {server_info} - {data.decode('utf-8')}")

import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b"Hello, server", ("127.0.0.1", 9090))
message, address = client.recvfrom(1024)
print(message.decode())

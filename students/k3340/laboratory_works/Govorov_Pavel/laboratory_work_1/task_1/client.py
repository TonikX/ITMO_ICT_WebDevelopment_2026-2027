import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b"Hello, server", ("127.0.0.1", 5001))
message, _ = client.recvfrom(1024)
print(message.decode())
client.close()

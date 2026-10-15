import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto(b'Hello, server', ('localhost', 30000))
answer, _ = client.recvfrom(1024)

print(answer)
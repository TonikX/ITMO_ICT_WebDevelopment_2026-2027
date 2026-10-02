import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Hello, server", ("127.0.0.1", 8081))

data, addr = sock.recvfrom(1024)
print(data.decode())
sock.close()
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b'Hello, server', ('localhost', 9090))
data = sock.recvfrom(1024)
print(f'Message from server: {data[0].decode('utf-8')}')
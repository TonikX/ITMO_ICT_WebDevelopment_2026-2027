import socket

PORT = 9090

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))
print(f'Server is listening on port {PORT}...')
data = sock.recvfrom(1024)
print(f'Message from client: {data[0].decode('utf-8')}')
sock.sendto(b'Hello, client', data[1])
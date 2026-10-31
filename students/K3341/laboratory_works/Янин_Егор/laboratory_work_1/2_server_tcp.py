import socket
import math

def pifagor(a, b):
    return math.sqrt(a ** 2 + b ** 2)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 9090))
sock.listen(1)
print('Server is listening on port 9090...')

while True:
    conn, addr = sock.accept()
    print(f'Connection from {addr}')
    data = conn.recv(1024)
    a, b = map(int, data.decode('utf-8').split())
    result = pifagor(a, b)
    conn.sendall(str(result).encode('utf-8'))
    conn.close()
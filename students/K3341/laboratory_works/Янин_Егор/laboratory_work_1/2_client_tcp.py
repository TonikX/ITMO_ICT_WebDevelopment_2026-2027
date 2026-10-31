import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9090))
a = int(input('Enter the first number: '))
b = int(input('Enter the second number: '))
sock.sendall(f'{a} {b}'.encode('utf-8'))
data = sock.recv(1024)
print(f'The result is: {data.decode("utf-8")}')
sock.close()
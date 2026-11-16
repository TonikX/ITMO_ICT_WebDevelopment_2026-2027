import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9090))

data = input("Введите через пробел длину основания и высоты паралеллограмма: ")
message = data.encode('utf-8')

sock.send(message)

S = sock.recv(1024)
result = S.decode('utf-8')

print(result)

sock.close()

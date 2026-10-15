import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(('localhost', 30_001))

info = client.recv(1024).decode('utf-8')
print(info)
data = input('Введите числа для рассчета -> ')
client.send(data.encode('utf-8'))
result = client.recv(1024)
print(result.decode('utf-8'))

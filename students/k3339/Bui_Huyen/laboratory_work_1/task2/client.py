import socket

HOST = '127.0.0.1'
PORT = 5001

# Создаем TCP сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Подключаемся к серверу
a = float(input('Введите а:'))
b = float(input('Введите b:'))

# Вводим длины катетов
message = f'{a} {b}'
client_socket.send(message.encode())

# Получаем результат от сервера
data = client_socket.recv(1024)
result = data.decode()
print('Гипотенуза:', result)

client_socket.close()
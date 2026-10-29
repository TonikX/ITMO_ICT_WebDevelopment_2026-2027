import socket

HOST = "127.0.0.1"
PORT = 5001

# Создаем TCP сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Привязываем сокет к адресу и порту
server_socket.bind((HOST, PORT))

# Начинаем прослушивание подключений
server_socket.listen()
print('Server is waitting for a connection...')

# Принимаем подключение клиента
connection, client_address = server_socket.accept()
print('Client connected:', client_address)

# Получаем данные
data = connection.recv(1024)
message = data.decode()

# Вычисляем гипотенузу
a, b = map(float, message.split())
c = (a**2 + b**2)**0.5

# Отправляем результат
connection.send(str(c).encode())

connection.close()
server_socket.close()
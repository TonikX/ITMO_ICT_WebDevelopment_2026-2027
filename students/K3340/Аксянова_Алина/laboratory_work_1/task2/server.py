import socket

HOST = "localhost"
PORT = 8081

# создаем сокет по протоколу TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# привязываем сокет к адресу и порту
server_socket.bind((HOST, PORT))

# начинаем слушать входящие подключения
server_socket.listen(1)

print(f"TCP-сервер запущен на {HOST}:{PORT}")

while True:
    # принимаем подключение от клиента
    client_connection, client_address = server_socket.accept()
    print(f"Подключение от {client_address}")

    # получаем данные от клиента
    data = client_connection.recv(1024).decode()

    # преобразуем полученные данные в числа
    a, b, h = map(float, data.split())

    # вычисляем площадь трапеции
    area = (a + b) * h / 2

    # отправляем результат клиенту
    client_connection.sendall(str(area).encode())

    # закрываем соединение с клиентом
    client_connection.close()
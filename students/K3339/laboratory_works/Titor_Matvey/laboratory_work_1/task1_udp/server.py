import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind(('localhost', 9000))
print('Сервер запущен на порту 9000...')

while True:
    data, client_address = server_socket.recvfrom(1024)
    print(f'Получено от {client_address}: {data.decode()}')

    server_socket.sendto('Hello, client'.encode(), client_address)
    print(f'Отправлено {client_address}: Hello, client')

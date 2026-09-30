import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 9001))
server_socket.listen(1)
print('Сервер запущен на порту 9001 (площадь трапеции)...')

while True:
    connection, client_address = server_socket.accept()
    print(f'Соединение от {client_address}')

    request = connection.recv(1024).decode()
    print(f'Запрос от клиента: {request}')

    parts = request.strip().split(';')
    if len(parts) != 3:
        response = 'Ошибка: нужно три числа через точку с запятой (a;b;h)'
    else:
        try:
            a = float(parts[0].replace(',', '.'))
            b = float(parts[1].replace(',', '.'))
            h = float(parts[2].replace(',', '.'))
        except ValueError:
            response = 'Ошибка: параметры должны быть числами'
        else:
            if a <= 0 or b <= 0 or h <= 0:
                response = 'Ошибка: числа должны быть положительными'
            else:
                area = (a + b) / 2 * h
                response = f'Площадь трапеции: {area}'

    connection.sendall(response.encode())
    print(f'Ответ клиенту: {response}')
    connection.close()

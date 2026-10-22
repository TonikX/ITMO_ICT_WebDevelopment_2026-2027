import socket
import math

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 30_001))
server.listen()

while True:
    socket_for_client, address = server.accept()
    text = 'Теорема Пифагора\nОтправьте данные в формате: \na, b, c' \
            '\t ,где c - гипотенуза. То что нужно найти отметьте * \n' \
            'Пример: 2, 3, *'
    socket_for_client.send(text.encode('utf-8'))
    try:
        data = socket_for_client.recv(1024).decode('utf-8').split(', ')
        if data[0] == '*':
            answer = math.sqrt( float(data[2]) ** 2 - float(data[1]) ** 2 )
            socket_for_client.send(str(answer).encode('utf-8'))
        elif data[1] == '*':
            answer = math.sqrt( float(data[2]) ** 2 - float(data[0]) ** 2 )
            socket_for_client.send(str(answer).encode('utf-8'))
        elif data[2] == '*':
            answer = math.sqrt(float(data[0]) ** 2 + float(data[1]) ** 2)
            socket_for_client.send(str(answer).encode('utf-8'))
        else:
            socket_for_client.send('Неверный формат, попробуйте еще раз'.encode('utf-8'))
        socket_for_client.close()
    except:
        socket_for_client.close()

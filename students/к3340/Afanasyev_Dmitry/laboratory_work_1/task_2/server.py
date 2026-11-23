import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 9999))
server.listen(5)

while True:
    client, addr = server.accept()
    with client, client.makefile('r', encoding='utf-8') as request:
        try:
            a, b, h = map(float, request.readline().split())
            result = str(h * (a + b) / 2)
        except ValueError:
            result = "Ошибка: введите три числа"
        client.sendall((result + '\n').encode())

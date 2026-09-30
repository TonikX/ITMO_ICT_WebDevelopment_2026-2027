import socket

HOST = 'localhost'
PORT = 8080

with open('index.html', 'rb') as f:
    page = f.read()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'HTTP-сервер запущен: http://{HOST}:{PORT}/')

while True:
    connection, client_address = server_socket.accept()
    print(f'Подключение от {client_address}')

    request = connection.recv(1024).decode()
    print(f'Запрос: {request.splitlines()[0]}')

    headers = (
        'HTTP/1.1 200 OK\r\n'
        'Content-Type: text/html; charset=utf-8\r\n'
        f'Content-Length: {len(page)}\r\n'
        'Connection: close\r\n'
        '\r\n'
    )
    connection.sendall(headers.encode() + page)

    connection.close()

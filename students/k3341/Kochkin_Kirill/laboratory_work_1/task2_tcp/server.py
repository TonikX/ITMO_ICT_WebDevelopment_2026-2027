import socket

# 4 вариант, площадь параллелограмма
HOST = "127.0.0.1"
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(
    (HOST, PORT)
)
server_socket.listen()

while True:
    client_socket, client_address = server_socket.accept()
    data = client_socket.recv(1024)
    parameters = data.decode()

    parameters = list(map(int, parameters.split(' ')))
    result = parameters[0] * parameters[1]

    client_socket.send(str(result).encode())
    client_socket.close()
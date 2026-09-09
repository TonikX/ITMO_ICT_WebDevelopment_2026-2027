import socket

HOST = "127.0.0.1"
PORT = 5000

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Сервер запущен: {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()

    print(f"Подключение клиента: {client_address}")

    try:
        data = client_socket.recv(1024).decode("utf-8")

        a, h = map(float, data.split())

        if a <= 0 or h <= 0:
            response = "Ошибка: основание и высота должны быть положительными"
        else:
            area = a * h
            response = str(area)

        client_socket.send(response.encode("utf-8"))

    except ValueError:
        response = "Ошибка: некорректные значения"
        client_socket.send(response.encode("utf-8"))

    finally:
        client_socket.close()
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8080))
server_socket.listen(1)
print("Сервер вычисления площади трапеции запущен на порту 8080...")

while True:
    client_connection, client_address = server_socket.accept()
    print(f"Подключение от {client_address}")

    request = client_connection.recv(1024).decode()
    print(f"Получены параметры от клиента: {request}")

    a_str, b_str, h_str = request.split()
    a = float(a_str)
    b = float(b_str)
    h = float(h_str)

    if a <= 0 or b <= 0 or h <= 0:
        response = "Основания и высота трапеции должны быть больше нуля"
    else:
        s = ((a + b) / 2) * h
        response = f"Площадь трапеции равна {s}"

    client_connection.sendall(response.encode())
    client_connection.close()
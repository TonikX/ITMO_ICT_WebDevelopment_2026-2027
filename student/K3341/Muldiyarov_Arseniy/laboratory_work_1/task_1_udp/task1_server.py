import socket

# Создаем UDP сокет (SOCK_DGRAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Привязываем сокет к локальному адресу и порту
server_address = ('localhost', 8080)
server_socket.bind(server_address)

print(f"UDP сервер запущен на {server_address}...")

while True:
    # recvfrom возвращает кортеж: (данные, адрес_отправителя)
    message, client_address = server_socket.recvfrom(1024)
    print(f"Получено от {client_address}: {message.decode('utf-8')}")

    # Формируем и отправляем ответ
    response = "Hello, client"
    server_socket.sendto(response.encode('utf-8'), client_address)
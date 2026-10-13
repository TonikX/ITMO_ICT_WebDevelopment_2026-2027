import socket

# Создаем UDP сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 8081))
print("UDP сервер запущен на порту 8081...")

while True:
    data, addr = server_socket.recvfrom(1024)
    print(f"Получено от клиента: {data.decode('utf-8')}")
    # Отправляем ответ
    server_socket.sendto(b"Hello, client", addr)

import socket

HOST = "127.0.0.1"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f"Сервер запущен на {HOST}:{PORT}")

while True:
    data, client_address = server_socket.recvfrom(1024)

    message = data.decode("utf-8")
    print(f"Получено от клиента: {message}")

    response = "Hello, client"
    server_socket.sendto(response.encode("utf-8"), client_address)
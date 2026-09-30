import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 8080))
print("UDP Сервер запущен на порту 8080...")

while True:
    data, client_address = server_socket.recvfrom(1024)
    message = data.decode()
    print(f"Получено от {client_address}: {message}")

    response = "Hello, client"
    server_socket.sendto(response.encode(), client_address)
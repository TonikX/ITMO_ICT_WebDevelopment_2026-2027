import socket

HOST = 'localhost'
PORT = 9001

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print(f"UDP-сервер запущен на {HOST}:{PORT}...")

while True:
    data, client_address = server_socket.recvfrom(1024)
    message = data.decode()
    print(f"Получено от {client_address}: {message}")

    response = "Hello, client"
    server_socket.sendto(response.encode(), client_address)

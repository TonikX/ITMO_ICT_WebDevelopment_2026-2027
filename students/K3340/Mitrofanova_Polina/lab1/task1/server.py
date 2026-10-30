import socket

HOST = '127.0.0.1'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f"UDP-сервер запущен на {HOST}:{PORT}...")

data, client_address = server_socket.recvfrom(1024)
print(f"Получено от клиента ({client_address}): {data.decode('utf-8')}")

response = "Hello, client"
server_socket.sendto(response.encode('utf-8'), client_address)

server_socket.close()
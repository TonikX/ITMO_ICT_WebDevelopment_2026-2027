import socket

HOST, PORT = "localhost", 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print(f"UDP-сервер запущен на {HOST}:{PORT}, жду сообщение...")

data, client_address = server_socket.recvfrom(1024)
print(f"Сообщение от клиента {client_address}: {data.decode('utf-8')}")

server_socket.sendto("Hello, client".encode("utf-8"), client_address)
server_socket.close()

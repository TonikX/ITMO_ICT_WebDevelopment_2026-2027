import socket

HOST = "127.0.0.1"
PORT = 8081

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))
print(f"UDP-сервер запущен на {HOST}:{PORT}")

while True:
    data, address = server.recvfrom(1024)
    print(f"Сообщение от {address}: {data.decode()}")
    server.sendto("Hello, client".encode(), address)

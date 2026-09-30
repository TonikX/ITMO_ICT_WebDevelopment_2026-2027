import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("127.0.0.1", 12345))

print("Сервер запущен. Ожидание сообщения...")

data, address = server.recvfrom(1024)

print("Сообщение от клиента:", data.decode("utf-8"))

server.sendto("Hello client".encode("utf-8"), address)

server.close()
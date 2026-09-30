import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 12345))
server.listen(1)

print("Сервер запущен. Ожидание подключения...")

connection, address = server.accept()
print("Клиент подключился")

data = connection.recv(1024).decode("utf-8")

a, b, h = map(float, data.split())

area = (a + b) * h / 2

connection.send(str(area).encode("utf-8"))

connection.close()
server.close()
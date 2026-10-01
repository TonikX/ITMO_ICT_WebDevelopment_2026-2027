import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 9002))
server.listen(1)

connection, _ = server.accept()
raw = connection.recv(1024).decode()
a, b, c = raw.split()
a = float(a)
b = float(b)
c = float(c)

d = b * b - 4 * a * c
if d > 0:
    x1 = (-b + d ** 0.5) / (2 * a)
    x2 = (-b - d ** 0.5) / (2 * a)
    result = f"Два корня: x1={x1:.2f}, x2={x2:.2f}"
elif d == 0:
    x1 = -b / (2 * a)
    result = f"Один корень: x={x1:.2f}"
else:
    result = "Действительных корней нет"

connection.send(result.encode())
connection.close()
server.close()
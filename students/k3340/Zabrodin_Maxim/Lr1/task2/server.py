import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5001))
server.listen(1)

print("Сервер запущен. Ожидание подключения.")

connection, address = server.accept()
print("Подключился клиент:", address)

reader = connection.makefile("r", encoding="utf-8")
data = reader.readline()

a, h = map(float, data.split())

if a <= 0 or h <= 0:
    result = "Основание и высота должны быть положительными"
else:
    area = a * h
    result = f"Площадь параллелограмма: {area}"

print(result)
connection.sendall((result + "\n").encode("utf-8"))

reader.close()
connection.close()
server.close()
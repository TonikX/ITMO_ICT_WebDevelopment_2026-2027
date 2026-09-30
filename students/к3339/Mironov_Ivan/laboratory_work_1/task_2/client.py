import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(("127.0.0.1", 12345))

a = float(input("Введите первое основание: "))
b = float(input("Введите второе основание: "))
h = float(input("Введите высоту: "))

message = f"{a} {b} {h}"

client.send(message.encode("utf-8"))

data = client.recv(1024).decode("utf-8")

print("Площадь трапеции:", data)

client.close()
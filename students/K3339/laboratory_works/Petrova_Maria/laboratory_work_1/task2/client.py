import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 8081))

a = float(input("Введите первое основание a: "))
b = float(input("Введите второе основание b: "))
h = float(input("Введите высоту h: "))

message = f"{a} {b} {h}"
client_socket.sendall(message.encode("utf-8"))
data = client_socket.recv(1024)

print("Площадь трапеции:", data.decode("utf-8"))

client_socket.close()
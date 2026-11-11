import socket

HOST = "localhost"
PORT = 8081

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

a = float(input("Введите первое основание трапеции: "))
b = float(input("Введите второе основание трапеции: "))
h = float(input("Введите высоту трапеции: "))

message = f"{a} {b} {h}"

client_socket.sendall(message.encode())

data = client_socket.recv(1024).decode()

print(f"Площадь трапеции: {data}")

client_socket.close()
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))

print("Площадь трапеции")
a = input("Первое основание трапеции (a): ")
b = input("Второе основание трапеции (b): ")
h = input("Введите высоту трапеции (h): ")

message = f"{a} {b} {h}"
client_socket.sendall(message.encode())
response = client_socket.recv(1024).decode()
print(f"Ответ от сервера: {response}")

client_socket.close()
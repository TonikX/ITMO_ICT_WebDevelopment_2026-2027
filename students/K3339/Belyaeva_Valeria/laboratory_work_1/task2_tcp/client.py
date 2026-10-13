import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8082))

a = input("Введите длину первого основания: ")
b = input("Введите длину второго основания: ")
h = input("Введите высоту: ")

client_socket.sendall(f"{a},{b},{h}".encode('utf-8'))
result = client_socket.recv(1024).decode('utf-8')
print(f"Площадь трапеции равна: {result}")
client_socket.close()

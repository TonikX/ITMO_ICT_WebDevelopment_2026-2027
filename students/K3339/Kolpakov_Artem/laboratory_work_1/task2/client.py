import socket

a = float(input("Введите длину основания: "))
h = float(input("Введите высоту: "))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8080))

data = f"{a} {h}"
client_socket.sendall(data.encode())

result = client_socket.recv(1024).decode()
print("Площадь параллелограмма:", result)

client_socket.close()
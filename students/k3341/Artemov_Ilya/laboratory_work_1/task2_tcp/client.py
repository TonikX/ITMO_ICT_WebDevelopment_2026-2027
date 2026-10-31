import socket

HOST = "localhost"
PORT = 9002

print("Теорема Пифагора: вычисление гипотенузы по двум катетам")
a = input("Введите катет a: ")
b = input("Введите катет b: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.sendall(f"{a} {b}".encode())

response = client_socket.recv(1024).decode()
print(f"Ответ от сервера: {response}")

client_socket.close()

import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('localhost', 8081))

a = input("введите a: ")
b = input("введите b: ")
c = input("введите c: ")

message = f"{a}, {b}, {c}"
client_socket.sendall(message.encode())

response = client_socket.recv(1024).decode()
print(f"получен ответ от сервера: {response}")

client_socket.close()
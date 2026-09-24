import socket

HOST = 'localhost'
PORT = 9002

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

base = input("Введите основание параллелограмма: ")
height = input("Введите высоту параллелограмма: ")

message = f"{base},{height}"
client_socket.sendall(message.encode())

response = client_socket.recv(1024).decode()
print(f"Ответ сервера: {response}")

client_socket.close()

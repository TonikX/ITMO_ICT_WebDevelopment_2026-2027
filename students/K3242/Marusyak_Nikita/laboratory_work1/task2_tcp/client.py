import socket

HOST = "127.0.0.1"
PORT = 5001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

a = float(input("Введите основание параллелограмма: "))
h = float(input("Введите высоту параллелограмма: "))

message = f"{a} {h}"

client_socket.send(message.encode("utf-8"))

result = client_socket.recv(1024).decode("utf-8")

print(result)

client_socket.close()

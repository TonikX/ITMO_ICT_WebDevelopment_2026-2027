import socket

HOST = "127.0.0.1"
PORT = 8080

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(
    (HOST, PORT)
)

parameters = input("Введите сторону и высоту параллелограмма через пробел: ")
client_socket.send(parameters.encode())

data = client_socket.recv(1024)
answer = data.decode()
print("Площадь параллелограмма: " + answer)

client_socket.close()
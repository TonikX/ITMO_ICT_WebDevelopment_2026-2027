import socket

HOST = "localhost"
PORT = 8081

# создаем сокет по протоколу TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# подключаемся к серверу
client_socket.connect((HOST, PORT))

# получаем параметры от пользователя
a = float(input("Введите первое основание трапеции: "))
b = float(input("Введите второе основание трапеции: "))
h = float(input("Введите высоту трапеции: "))

# формируем сообщение для сервера
message = f"{a} {b} {h}"

# отправляем данные серверу
client_socket.sendall(message.encode())

# получаем результат от сервера
data = client_socket.recv(1024).decode()

print(f"Площадь трапеции: {data}")

# закрываем сокет
client_socket.close()
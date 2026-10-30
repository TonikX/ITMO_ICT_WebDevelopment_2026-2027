import socket 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

client_socket.connect(('localhost', 8080))
print("Введи 3 числа для квадратного уравнения в 1 строчку через пробел:")
parameters = input()
client_socket.sendall(parameters.encode())

response = client_socket.recv(1024).decode()
print(f'Ответ от сервера: {response}')

client_socket.close()

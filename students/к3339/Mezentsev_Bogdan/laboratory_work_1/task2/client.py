import socket


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8081))

coefficients = input("Введите коэффициенты a,b,c через запятую: ")
client_socket.sendall(coefficients.encode())

result = client_socket.recv(1024).decode()
print(f"Ответ сервера: {result}")

client_socket.close()

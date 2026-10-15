import socket

input_data = input("Введите числа A и B: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))

client_socket.sendall(input_data.encode())

response = client_socket.recv(1024).decode()
print(f"Гипотенуза: {response}")

client_socket.close()
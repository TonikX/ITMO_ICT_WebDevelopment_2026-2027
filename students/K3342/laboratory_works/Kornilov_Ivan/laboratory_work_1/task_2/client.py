import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8080))

parameters = input()
client_socket.sendall(parameters.encode("utf-8"))

print(client_socket.recv(1024).decode("utf-8"))
client_socket.close()

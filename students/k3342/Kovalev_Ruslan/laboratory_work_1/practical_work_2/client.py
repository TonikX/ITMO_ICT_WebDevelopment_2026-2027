import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 9090))

a = input("a: ")
b = input("b: ")
h = input("h: ")

client_socket.send(f"{a},{b},{h}".encode('utf-8'))

result = client_socket.recv(1024).decode('utf-8')
print(result)

client_socket.close()
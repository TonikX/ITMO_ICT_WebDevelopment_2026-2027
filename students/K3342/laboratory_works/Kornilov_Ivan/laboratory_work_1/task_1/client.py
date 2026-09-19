import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto("Hello, server".encode("utf-8"), ("localhost", 8080))

data = client_socket.recv(1024)
print(data.decode("utf-8"))

client_socket.close()

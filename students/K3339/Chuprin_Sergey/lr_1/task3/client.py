import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(('localhost', 30_002))

print(client.recv(1024).decode('utf-8'))

client.close()

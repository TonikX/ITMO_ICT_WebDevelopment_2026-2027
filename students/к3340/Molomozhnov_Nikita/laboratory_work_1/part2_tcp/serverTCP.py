import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5011))
server.listen(1)
client_socket, client_address = server.accept()
data = client_socket.recv(1024).decode('utf-8')
a, b, h = map(float, data.split(','))
area = (a + b) / 2 * h
print(f"Площадь трапеции: {area}")
response = f"Площадь трапеции: {area}"
client_socket.send(response.encode('utf-8'))
client_socket.close()
server.close()
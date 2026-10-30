import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 8081))

server_socket.listen(1)

client_socket, client_address = server_socket.accept()

data = client_socket.recv(1024)
message = data.decode("utf-8")
a, b, h = map(float, message.split())
area = (a + b) / 2 * h

client_socket.sendall(str(area).encode("utf-8"))

server_socket.close()
client_socket.close()
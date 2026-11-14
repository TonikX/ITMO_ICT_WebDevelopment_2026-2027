import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 9090))
server_socket.listen(1)

conn, addr = server_socket.accept()

data = conn.recv(1024).decode('utf-8')
a, b, h = map(float, data.split(','))

area = ((a + b) / 2) * h

conn.send(str(area).encode('utf-8'))

conn.close()
server_socket.close()
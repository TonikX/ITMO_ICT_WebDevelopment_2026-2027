import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 8082))
sock.listen(1)

conn, addr = sock.accept()

data = conn.recv(1024).decode()
a, h = data.split()
a = float(a)
h = float(h)
s = a * h

conn.send(str(s).encode())
conn.close()
sock.close()
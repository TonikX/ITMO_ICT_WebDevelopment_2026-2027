import socket

a = input("Введите основание a: ")
h = input("Введите высоту h: ")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 8082))

sock.send((a + " " + h).encode())

data = sock.recv(1024).decode()
print("Площадь параллелограмма: " + data)
sock.close()
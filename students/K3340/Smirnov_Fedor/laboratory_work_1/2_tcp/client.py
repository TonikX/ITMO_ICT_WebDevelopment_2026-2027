import socket

ADDRESS = ("localhost", 5002)

print("Площадь трапеции: S = (a + b) / 2 * h")
a = input("Основание a: ")
b = input("Основание b: ")
h = input("Высота h: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(ADDRESS)
    sock.sendall(f"{a} {b} {h}".encode())
    print(sock.recv(1024).decode())

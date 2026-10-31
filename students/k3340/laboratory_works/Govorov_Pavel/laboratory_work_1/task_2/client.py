import socket

a = float(input("Катет a: "))
b = float(input("Катет b: "))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5002))
client.sendall(f"{a} {b}".encode())
print("Гипотенуза:", client.recv(1024).decode())
client.close()

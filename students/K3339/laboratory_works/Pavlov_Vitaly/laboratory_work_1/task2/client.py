import socket

SERVER = ("127.0.0.1", 8082)


def read_number(name):
    while True:
        try:
            return float(input(f"{name} = "))
        except ValueError:
            print("Нужно ввести число")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(SERVER)
print("Решение квадратного уравнения ax^2 + bx + c = 0")

while True:
    a = read_number("a")
    b = read_number("b")
    c = read_number("c")
    client.sendall(f"{a} {b} {c}".encode())
    print("Ответ сервера:", client.recv(1024).decode())
    if input("Ещё раз? (y/n): ").lower() != "y":
        break

client.close()

import socket

HOST = "127.0.0.1"
PORT = 5001

print("Решение квадратного уравнения")
print("Уравнение имеет вид: ax^2 + bx + c = 0")

a = float(input("Введите a: "))
b = float(input("Введите b: "))
c = float(input("Введите c: "))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

message = f"{a} {b} {c}"

client_socket.sendall(message.encode("utf-8"))

data = client_socket.recv(4096)

result = data.decode("utf-8")

print("\nРезультат:")
print(result)

client_socket.close()
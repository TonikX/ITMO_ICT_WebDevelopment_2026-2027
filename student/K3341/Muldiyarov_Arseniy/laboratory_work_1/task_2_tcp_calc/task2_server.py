import socket
import json
import math


def calculate(variant, params):
    if variant == 1:  # Пифагор
        a, b = params
        return math.sqrt(a ** 2 + b ** 2)
    elif variant == 2:  # Квадратное уравнение (ax^2 + bx + c = 0)
        a, b, c = params
        d = b ** 2 - 4 * a * c
        if d < 0: return "Действительных корней нет"
        x1 = (-b + math.sqrt(d)) / (2 * a)
        x2 = (-b - math.sqrt(d)) / (2 * a)
        return f"x1 = {x1:.2f}, x2 = {x2:.2f}"
    elif variant == 3:  # Трапеция
        a, b, h = params
        return ((a + b) / 2) * h
    elif variant == 4:  # Параллелограмм
        a, h = params
        return a * h

MY_VARIANT = 2

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8081))
server_socket.listen(1)
print("TCP сервер запущен, жду подключения...")

conn, addr = server_socket.accept()
print(f"Клиент {addr} подключился.")

try:
    while True:
        data = conn.recv(1024).decode('utf-8')
        if not data: break

        params = json.loads(data)
        result = calculate(MY_VARIANT, params)

        conn.sendall(json.dumps({"result": str(result)}).encode('utf-8'))
except ConnectionResetError:
    print("Клиент отключился.")
finally:
    conn.close()
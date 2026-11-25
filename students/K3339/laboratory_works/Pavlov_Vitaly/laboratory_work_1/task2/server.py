import math
import socket

HOST = "127.0.0.1"
PORT = 8082


def solve(a, b, c):
    if a == 0:
        return "a = 0, уравнение не квадратное"
    d = b * b - 4 * a * c
    if d < 0:
        return f"D = {d:g}, действительных корней нет"
    if d == 0:
        x = -b / (2 * a) + 0.0
        return f"D = 0, x = {x:g}"
    x1 = (-b + math.sqrt(d)) / (2 * a)
    x2 = (-b - math.sqrt(d)) / (2 * a)
    return f"D = {d:g}, x1 = {x1:g}, x2 = {x2:g}"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"TCP-сервер запущен на {HOST}:{PORT}")

while True:
    conn, address = server.accept()
    print(f"Подключился {address}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                a, b, c = map(float, data.decode().split())
                answer = solve(a, b, c)
            except ValueError:
                answer = "Ошибка: нужно передать три числа"
            print(f"{data.decode()} -> {answer}")
            conn.sendall(answer.encode())
    except ConnectionError:
        pass
    conn.close()
    print(f"Отключился {address}")

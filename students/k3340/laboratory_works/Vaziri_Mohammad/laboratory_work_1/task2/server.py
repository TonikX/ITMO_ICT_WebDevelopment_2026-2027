"""Задание 2 (вариант 2). TCP-сервер решает квадратное уравнение ax^2 + bx + c = 0.

Протокол: клиент присылает одну строку «a b c», сервер отвечает одной строкой с результатом.
"""
import math
import socket

HOST, PORT = "127.0.0.1", 9092


def solve_quadratic(a: float, b: float, c: float) -> str:
    if a == 0:                                  # вырожденный случай: линейное уравнение bx + c = 0
        if b == 0:
            return "Бесконечно много решений" if c == 0 else "Решений нет"
        return f"Линейное уравнение, x = {-c / b:g}"
    d = b * b - 4 * a * c                       # дискриминант
    if d > 0:
        x1 = (-b + math.sqrt(d)) / (2 * a)
        x2 = (-b - math.sqrt(d)) / (2 * a)
        return f"D = {d:g}; два корня: x1 = {x1:g}, x2 = {x2:g}"
    if d == 0:
        return f"D = 0; один корень: x = {-b / (2 * a):g}"
    re, im = -b / (2 * a) + 0.0, math.sqrt(-d) / (2 * abs(a))  # + 0.0 убирает «-0»
    return f"D = {d:g} < 0; действительных корней нет (комплексные: {re:g} ± {im:g}i)"


def handle(conn: socket.socket) -> None:
    data = conn.recv(1024).decode("utf-8").strip()
    try:
        a, b, c = map(float, data.replace(",", ".").split())
        answer = solve_quadratic(a, b, c)
    except ValueError:
        answer = "Ошибка: нужно отправить три числа a b c"
    conn.sendall(answer.encode("utf-8"))


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:   # SOCK_STREAM = TCP
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"TCP-сервер слушает {HOST}:{PORT}")
        while True:
            conn, addr = srv.accept()            # для каждого клиента — новое соединение
            with conn:
                print(f"Подключился {addr}")
                handle(conn)


if __name__ == "__main__":
    main()

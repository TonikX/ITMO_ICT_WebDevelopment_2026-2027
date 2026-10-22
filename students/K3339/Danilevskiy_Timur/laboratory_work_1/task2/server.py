"""Задание 2 (вариант 3). TCP-сервер, вычисляющий площадь трапеции.

Протокол: клиент присылает строку "a b h" (основания и высота через пробел),
сервер отвечает строкой с результатом или с описанием ошибки.
"""
import socket

HOST = "127.0.0.1"
PORT = 9091
BUFFER_SIZE = 1024


def trapezoid_area(a, b, h):
    return (a + b) / 2 * h


def handle_request(data):
    try:
        a, b, h = map(float, data.split())
    except ValueError:
        return "Ошибка: нужно передать три числа через пробел: a b h"

    if a <= 0 or b <= 0 or h <= 0:
        return "Ошибка: основания и высота должны быть положительными"

    return f"Площадь трапеции: {trapezoid_area(a, b, h):.2f}"


def main():
    # SOCK_STREAM — потоковый сокет, то есть TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"TCP-сервер запущен на {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with conn:
                data = conn.recv(BUFFER_SIZE).decode("utf-8")
                print(f"Запрос от {addr[0]}:{addr[1]}: {data!r}")

                response = handle_request(data)
                conn.sendall(response.encode("utf-8"))
                print(f"Ответ: {response}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен")

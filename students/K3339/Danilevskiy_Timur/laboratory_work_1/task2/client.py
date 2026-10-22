"""Задание 2 (вариант 3). TCP-клиент: запрашивает у сервера площадь трапеции."""
import socket

HOST = "127.0.0.1"
PORT = 9091
BUFFER_SIZE = 1024


def read_positive(prompt):
    while True:
        try:
            value = float(input(prompt).replace(",", "."))
        except ValueError:
            print("Введите число")
            continue
        if value > 0:
            return value
        print("Значение должно быть положительным")


def main():
    print("Площадь трапеции: S = (a + b) / 2 * h")
    a = read_positive("Основание a: ")
    b = read_positive("Основание b: ")
    h = read_positive("Высота h: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError:
            print("Сервер недоступен")
            return

        sock.sendall(f"{a} {b} {h}".encode("utf-8"))
        print(sock.recv(BUFFER_SIZE).decode("utf-8"))


if __name__ == "__main__":
    main()

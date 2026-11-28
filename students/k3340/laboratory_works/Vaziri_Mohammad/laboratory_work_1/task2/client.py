"""Задание 2 (вариант 2). TCP-клиент: пользователь вводит a, b, c, сервер возвращает решение."""
import socket

HOST, PORT = "127.0.0.1", 9092


def read_number(name: str) -> float:
    while True:
        raw = input(f"Введите {name}: ").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            print("Это не число, попробуйте ещё раз.")


def main():
    print("Решение квадратного уравнения a*x^2 + b*x + c = 0")
    a, b, c = read_number("a"), read_number("b"), read_number("c")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(f"{a} {b} {c}".encode("utf-8"))
        print("Ответ сервера:", sock.recv(1024).decode("utf-8"))


if __name__ == "__main__":
    main()

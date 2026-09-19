from __future__ import annotations

import math
import socket

HOST = "127.0.0.1"
PORT = 8082
BUFFER_SIZE = 1024


def solve_quadratic(a: float, b: float, c: float) -> str:
    if a == 0:
        if b == 0:
            if c == 0:
                return "Бесконечно много решений (0 = 0)"
            return "Решений нет (противоречие)"
        x = -c / b
        return f"Линейное уравнение: x = {x}"

    discriminant = b * b - 4 * a * c
    if discriminant > 0:
        sqrt_d = math.sqrt(discriminant)
        x1 = (-b + sqrt_d) / (2 * a)
        x2 = (-b - sqrt_d) / (2 * a)
        return f"Два корня: x1 = {x1}, x2 = {x2} (D = {discriminant})"
    if discriminant == 0:
        x = -b / (2 * a)
        return f"Один корень: x = {x} (D = 0)"
    return f"Действительных корней нет (D = {discriminant})"


def handle_client(conn: socket.socket, address: tuple[str, int]) -> None:
    print(f"Подключился клиент {address}")
    with conn:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            return

        raw = data.decode("utf-8").strip()
        print(f"Получено от {address}: {raw}")

        try:
            parts = raw.replace(",", " ").split()
            if len(parts) != 3:
                raise ValueError("нужно ровно 3 числа: a b c")
            a, b, c = map(float, parts)
            result = solve_quadratic(a, b, c)
        except ValueError as exc:
            result = f"Ошибка ввода: {exc}"

        conn.sendall(result.encode("utf-8"))
        print(f"Ответ клиенту {address}: {result}")


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"TCP-сервер (квадратное уравнение) на {HOST}:{PORT}")

        while True:
            conn, address = server.accept()
            handle_client(conn, address)


if __name__ == "__main__":
    main()

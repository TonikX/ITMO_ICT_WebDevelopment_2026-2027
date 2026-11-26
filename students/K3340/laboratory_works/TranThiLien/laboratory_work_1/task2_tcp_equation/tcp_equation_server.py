import socket
import math

HOST = "127.0.0.1"
PORT = 5001


def solve_quadratic(a, b, c):
    if a == 0:
        if b == 0:
            if c == 0:
                return "Уравнение имеет бесконечно много решений."
            return "Уравнение не имеет решений."

        x = -c / b
        return f"Это линейное уравнение. x = {x:.6f}"

    discriminant = b ** 2 - 4 * a * c

    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)

        return (
            f"Дискриминант D = {discriminant:.6f}\n"
            f"x1 = {x1:.6f}\n"
            f"x2 = {x2:.6f}"
        )

    elif discriminant == 0:
        x = -b / (2 * a)

        return (
            f"Дискриминант D = 0\n"
            f"x = {x:.6f}"
        )

    else:
        return (
            f"Дискриминант D = {discriminant:.6f}\n"
            "Действительных корней нет."
        )


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"TCP server запущен на {HOST}:{PORT}")

while True:
    connection, client_address = server_socket.accept()

    print(f"Подключен клиент: {client_address}")

    try:
        data = connection.recv(1024).decode("utf-8")

        a, b, c = map(float, data.split())

        print(f"Получены коэффициенты: a={a}, b={b}, c={c}")

        result = solve_quadratic(a, b, c)

        connection.sendall(result.encode("utf-8"))

    except ValueError:
        connection.sendall(
            "Ошибка: необходимо передать три числа a, b и c."
            .encode("utf-8")
        )

    finally:
        connection.close()
        print("Соединение закрыто.")
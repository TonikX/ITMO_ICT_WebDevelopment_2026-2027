import math
import socket


HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 1024


def solve_quadratic_equation(a: float, b: float, c: float) -> str:
    if a == 0:
        return "Ошибка: коэффициент a не должен быть равен нулю"

    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        return f"Дискриминант D = {discriminant:g}. Действительных корней нет"

    if math.isclose(discriminant, 0.0):
        root = -b / (2 * a)
        return f"Дискриминант D = 0. Один корень: x = {root:g}"

    first_root = (-b + math.sqrt(discriminant)) / (2 * a)
    second_root = (-b - math.sqrt(discriminant)) / (2 * a)
    return (
        f"Дискриминант D = {discriminant:g}. "
        f"Два корня: x1 = {first_root:g}, x2 = {second_root:g}"
    )


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"TCP server is listening on {HOST}:{PORT}")

        connection, client_address = server_socket.accept()
        with connection:
            print(f"Client connected: {client_address}")
            request = connection.recv(BUFFER_SIZE).decode("utf-8")
            print(f"Received coefficients: {request}")

            try:
                a_text, b_text, c_text = request.split(";")
                a = float(a_text)
                b = float(b_text)
                c = float(c_text)
                response = solve_quadratic_equation(a, b, c)
            except (ValueError, TypeError):
                response = "Ошибка: необходимо передать три числа в формате a;b;c"

            connection.sendall(response.encode("utf-8"))
            print(f"Sent result: {response}")


if __name__ == "__main__":
    main()

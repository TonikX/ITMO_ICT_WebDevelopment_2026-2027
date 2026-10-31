import socket

ADDRESS = ("localhost", 5002)


def trapezoid_area(a, b, h):
    return (a + b) / 2 * h


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(ADDRESS)
    sock.listen()
    print("TCP-сервер запущен на", ADDRESS)

    while True:
        conn, address = sock.accept()
        with conn:
            request = conn.recv(1024).decode()
            print(f"{address}: {request}")

            try:
                a, b, h = map(float, request.split())
                if min(a, b, h) <= 0:
                    answer = "Ошибка: основания и высота должны быть больше нуля"
                else:
                    answer = f"Площадь трапеции: {trapezoid_area(a, b, h)}"
            except ValueError:
                answer = "Ошибка: нужно передать три числа"

            conn.sendall(answer.encode())

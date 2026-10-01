import math
import socket

HOST, PORT = "127.0.0.1", 5001


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"TCP-сервер запущен на {HOST}:{PORT}")

        while True:
            connection, _ = server.accept()

            with connection:
                try:
                    a, b = map(float, connection.recv(1024).decode().split())

                    if a <= 0 or b <= 0:
                        raise ValueError

                    answer = str(math.hypot(a, b))
                except ValueError:
                    answer = "Ошибка: введите два положительных числа"

                connection.sendall(answer.encode())


if __name__ == "__main__":
    run_server()

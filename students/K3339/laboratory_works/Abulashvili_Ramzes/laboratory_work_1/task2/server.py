import math
import socket

HOST = "127.0.0.1"
PORT = 5002


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"TCP-сервер: {HOST}:{PORT}", flush=True)
        while True:
            connection, address = server.accept()
            with connection:
                connection.settimeout(5)
                try:
                    with connection.makefile("rb") as reader:
                        data = reader.readline()
                    if not data.endswith(b"\n"):
                        continue
                    try:
                        request = data.decode("utf-8").strip()
                        print(f"Получено от {address[0]}: {request}", flush=True)
                        a, b = map(float, request.split())
                        c = math.hypot(a, b)
                        if not all(math.isfinite(value) and value > 0 for value in (a, b, c)):
                            raise ValueError
                        response = f"Гипотенуза: {c:g}"
                    except ValueError:
                        response = "Ошибка: введите два положительных конечных катета."
                    connection.sendall((response + "\n").encode("utf-8"))
                    print(response, flush=True)
                except OSError:
                    pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    except OSError as error:
        print(f"Ошибка сервера: {error}")

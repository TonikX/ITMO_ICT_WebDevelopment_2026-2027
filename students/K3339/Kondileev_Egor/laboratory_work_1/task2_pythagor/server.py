"""Задание 2: TCP-сервер для теоремы Пифагора."""
import json
import math
import socket

HOST = "127.0.0.1"
PORT = 5002
BUFFER_SIZE = 4096

def receive_line(connection):
    data = bytearray()
    while True:
        part = connection.recv(1)
        if not part:
            return None
        if part == b"\n":
            return data.decode("utf-8")
        data.extend(part)
        if len(data) > BUFFER_SIZE:
            raise ValueError("Слишком длинный запрос")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"TCP-сервер запущен на {HOST}:{PORT}. Ожидаю клиента...")

        while True:
            connection, address = server.accept()
            with connection:
                print(f"Подключился клиент: {address}")
                try:
                    request_line = receive_line(connection)
                    if request_line is None:
                        continue
                    request = json.loads(request_line)
                    a = float(request["a"])
                    b = float(request["b"])

                    if a < 0 or b < 0:
                        response = {"ok": False, "error": "Катеты не могут быть отрицательными."}
                    else:
                        c = math.sqrt(a * a + b * b)
                        response = {"ok": True, "a": a, "b": b, "c": c}
                except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
                    response = {"ok": False, "error": f"Некорректные данные: {error}"}

                connection.sendall((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))
                print(f"Ответ отправлен клиенту: {response}")

if __name__ == "__main__":
    main()

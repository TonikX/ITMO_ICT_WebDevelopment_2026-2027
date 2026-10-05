import json
import math
import socket


HOST = "127.0.0.1"
PORT = 5002
BUFFER_SIZE = 4096


def calculate_hypotenuse(data):
    a = float(data["a"])
    b = float(data["b"])

    if a <= 0 or b <= 0:
        raise ValueError("Катеты должны быть положительными числами")

    return {"c": math.sqrt(a**2 + b**2)}


def handle_request(raw_data):
    request = json.loads(raw_data)
    return calculate_hypotenuse(request)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Сервер запущен, слушаю {HOST}:{PORT}")
        print("Вариант 1: теорема Пифагора")

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"Connection from {client_address}")
                raw_data = client_socket.recv(BUFFER_SIZE).decode("utf-8")

                try:
                    result = {"status": "ok", "result": handle_request(raw_data)}
                except (ValueError, KeyError, json.JSONDecodeError) as error:
                    result = {"status": "error", "message": str(error)}

                client_socket.sendall(json.dumps(result, ensure_ascii=False).encode("utf-8"))


if __name__ == "__main__":
    main()

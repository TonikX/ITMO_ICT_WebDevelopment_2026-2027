import json
import socket


HOST = "127.0.0.1"
PORT = 5002
BUFFER_SIZE = 4096


def read_float(prompt):
    return float(input(prompt).replace(",", "."))


def main():
    print("Вариант 1: теорема Пифагора")
    a = read_float("Введите первый катет: ")
    b = read_float("Введите второй катет: ")
    request = {"a": a, "b": b}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(json.dumps(request).encode("utf-8"))

        response = client_socket.recv(BUFFER_SIZE).decode("utf-8")
        data = json.loads(response)

        if data["status"] == "ok":
            print(f"Гипотенуза: {data['result']['c']}")
        else:
            print(f"Ошибка: {data['message']}")


if __name__ == "__main__":
    main()

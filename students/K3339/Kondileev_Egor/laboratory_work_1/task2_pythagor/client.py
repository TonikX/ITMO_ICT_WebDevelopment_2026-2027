"""Задание 2: TCP-клиент для теоремы Пифагора."""
import json
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002

def receive_line(connection):
    data = bytearray()
    while True:
        part = connection.recv(1)
        if not part:
            raise ConnectionError("Сервер закрыл соединение без ответа.")
        if part == b"\n":
            return data.decode("utf-8")
        data.extend(part)

def main():
    print("Теорема Пифагора: c = sqrt(a² + b²)")
    raw_a = input("Введите катет a (или q для выхода): ").strip()
    if raw_a.lower() == "q":
        print("Выход.")
        return

    raw_b = input("Введите катет b: ").strip()
    try:
        a = float(raw_a)
        b = float(raw_b)
    except ValueError:
        print("Ошибка: нужно вводить числа, например 3 и 4.")
        return

    request = {"a": a, "b": b}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((SERVER_HOST, SERVER_PORT))
            client.sendall((json.dumps(request) + "\n").encode("utf-8"))
            response = json.loads(receive_line(client))

        if response.get("ok"):
            print(f"Сервер получил a={response['a']} и b={response['b']}")
            print(f"Гипотенуза c = {response['c']:.6g}")
        else:
            print(f"Сервер сообщил об ошибке: {response.get('error', 'неизвестная ошибка')}")
    except ConnectionRefusedError:
        print("Не удалось подключиться. Сначала запустите сервер.")
    except OSError as error:
        print(f"Сетевая ошибка: {error}")

if __name__ == "__main__":
    main()

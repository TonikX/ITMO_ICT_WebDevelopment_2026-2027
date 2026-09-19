import socket

HOST = "127.0.0.1"
PORT = 8082
BUFFER_SIZE = 1024


def main() -> None:
    print("Решение квадратного уравнения ax² + bx + c = 0")
    a = input("Введите a: ").strip()
    b = input("Введите b: ").strip()
    c = input("Введите c: ").strip()
    payload = f"{a} {b} {c}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        client.sendall(payload.encode("utf-8"))
        response = client.recv(BUFFER_SIZE).decode("utf-8")
        print(f"Ответ сервера: {response}")


if __name__ == "__main__":
    main()

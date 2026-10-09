import socket


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 1024


def main() -> None:
    base = float(input("Введите длину основания параллелограмма: "))
    height = float(input("Введите высоту параллелограмма: "))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        print("Подключение к серверу установлено")

        message = f"{base} {height}"
        client_socket.sendall(message.encode("utf-8"))

        data = client_socket.recv(BUFFER_SIZE)
        area = data.decode("utf-8")

        print(f"Площадь параллелограмма: {area}")


if __name__ == "__main__":
    main()
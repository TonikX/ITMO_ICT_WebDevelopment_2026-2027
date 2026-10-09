import socket


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        message = "Hello, server"

        client_socket.sendto(
            message.encode("utf-8"),
            (SERVER_HOST, SERVER_PORT),
        )

        print(f"Отправлено серверу: {message}")

        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        response = data.decode("utf-8")

        print(f"Получено от сервера: {response}")


if __name__ == "__main__":
    main()
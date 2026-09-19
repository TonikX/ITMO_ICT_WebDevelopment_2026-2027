import socket

HOST = "127.0.0.1"
PORT = 8081
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        message = "Hello, server"
        client.sendto(message.encode("utf-8"), (HOST, PORT))
        print(f"Отправлено серверу: {message}")

        data, _ = client.recvfrom(BUFFER_SIZE)
        print(f"Получено от сервера: {data.decode('utf-8')}")


if __name__ == "__main__":
    main()

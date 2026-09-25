import socket


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))

        print(f"UDP-сервер запущен на {HOST}:{PORT}")
        print("Ожидание сообщения от клиента...")

        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        message = data.decode("utf-8")

        print(f"Получено от клиента: {message}")

        response = "Hello, client"
        server_socket.sendto(response.encode("utf-8"), client_address)

        print(f"Ответ отправлен клиенту: {response}")


if __name__ == "__main__":
    main()
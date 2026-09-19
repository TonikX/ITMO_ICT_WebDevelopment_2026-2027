import socket

HOST = "127.0.0.1"
PORT = 8081
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((HOST, PORT))
        print(f"UDP-сервер запущен на {HOST}:{PORT}")

        while True:
            data, address = server.recvfrom(BUFFER_SIZE)
            message = data.decode("utf-8")
            print(f"Получено от {address}: {message}")

            reply = "Hello, client"
            server.sendto(reply.encode("utf-8"), address)
            print(f"Отправлено клиенту {address}: {reply}")


if __name__ == "__main__":
    main()

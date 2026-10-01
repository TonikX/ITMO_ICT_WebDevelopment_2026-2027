import socket


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(("127.0.0.1", 5001))
        print("UDP-сервер запущен: 127.0.0.1:5001")
        while True:
            data, address = server.recvfrom(1024)
            print(data.decode("utf-8", errors="replace"))
            server.sendto("Hello, client".encode("utf-8"), address)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    except OSError as error:
        print(f"Ошибка сети: {error}")

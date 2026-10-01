import socket


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(5)
        client.sendto("Hello, server".encode("utf-8"), ("127.0.0.1", 5001))
        data, address = client.recvfrom(1024)
        print(data.decode("utf-8"))


if __name__ == "__main__":
    try:
        main()
    except socket.timeout:
        print("Сервер не ответил. Сначала запустите server.py.")
    except OSError as error:
        print(f"Ошибка сети: {error}. Проверьте, запущен ли server.py.")

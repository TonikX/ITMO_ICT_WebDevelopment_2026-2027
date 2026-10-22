"""Задание 1. UDP-сервер: принимает "Hello, server" и отвечает "Hello, client"."""
import socket

HOST = "127.0.0.1"
PORT = 9090
BUFFER_SIZE = 1024


def main():
    # SOCK_DGRAM — датаграммный сокет, то есть UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, PORT))
        print(f"UDP-сервер запущен на {HOST}:{PORT}")

        while True:
            # UDP не устанавливает соединение: каждая датаграмма приходит
            # вместе с адресом отправителя, по нему и отвечаем
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Сообщение от {addr[0]}:{addr[1]}: {data.decode('utf-8')}")
            sock.sendto("Hello, client".encode("utf-8"), addr)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен")

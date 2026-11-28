"""Задание 1. UDP-клиент: отправляет «Hello, server» и печатает ответ сервера."""
import socket

HOST, PORT = "127.0.0.1", 9091


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)                             # UDP не гарантирует доставку — не ждём вечно
        sock.sendto("Hello, server".encode("utf-8"), (HOST, PORT))
        data, _ = sock.recvfrom(1024)
        print(f"Ответ сервера: {data.decode('utf-8')}")


if __name__ == "__main__":
    main()

"""Задание 1. UDP-клиент: отправляет "Hello, server" и выводит ответ сервера."""
import socket

HOST = "127.0.0.1"
PORT = 9090
BUFFER_SIZE = 1024
TIMEOUT = 5


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # UDP не гарантирует доставку, поэтому ждём ответ не бесконечно
        sock.settimeout(TIMEOUT)
        sock.sendto("Hello, server".encode("utf-8"), (HOST, PORT))

        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print(f"Сервер не ответил за {TIMEOUT} с")
            return

        print(f"Ответ от сервера {addr[0]}:{addr[1]}: {data.decode('utf-8')}")


if __name__ == "__main__":
    main()

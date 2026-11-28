"""Задание 4. Клиент чата. Один скрипт для всех пользователей: имя вводится при запуске.

Приём сообщений идёт в отдельном потоке, чтобы можно было одновременно читать и писать.
"""
import socket
import sys
import threading

HOST, PORT = "127.0.0.1", 9094


def receive(sock: socket.socket) -> None:
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break
        if not data:
            print("Соединение с сервером закрыто")
            break
        sys.stdout.write(data.decode("utf-8"))
        sys.stdout.flush()


def main():
    name = input("Ваше имя: ").strip()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.sendall(name.encode("utf-8"))
    threading.Thread(target=receive, args=(sock,), daemon=True).start()
    try:
        while True:
            text = input()
            sock.sendall(text.encode("utf-8"))
            if text.strip() == "/exit":
                break
    except (EOFError, KeyboardInterrupt):
        sock.sendall(b"/exit")
    finally:
        sock.close()


if __name__ == "__main__":
    main()

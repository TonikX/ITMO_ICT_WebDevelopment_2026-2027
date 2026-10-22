"""Задание 4. Многопользовательский TCP-чат: клиент.

Один и тот же скрипт запускается каждым пользователем в отдельном процессе.
Главный поток читает ввод с клавиатуры и отправляет сообщения,
отдельный поток принимает сообщения от сервера и печатает их.
"""
import os
import socket
import threading

HOST = "127.0.0.1"
PORT = 9092


def send_line(sock, text):
    sock.sendall((text + "\n").encode("utf-8"))


def register(sock, reader):
    """Спрашивает имя, пока сервер его не примет."""
    while True:
        name = input("Введите имя: ").strip()
        send_line(sock, name)
        answer = reader.readline().strip()

        if answer == "NAME_OK":
            return name
        if answer == "NAME_TAKEN":
            print("Это имя уже занято, выберите другое")
        elif answer == "NAME_EMPTY":
            print("Имя не может быть пустым")
        else:
            raise ConnectionError("сервер закрыл соединение")


def receive(reader, leaving):
    for line in reader:
        print(line.rstrip("\n"))

    if not leaving.is_set():
        # Сервер закрыл соединение сам. Главный поток заблокирован в input(),
        # поэтому завершаем процесс целиком
        print("Соединение с сервером потеряно")
        os._exit(1)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Сервер недоступен")
        return

    reader = sock.makefile("r", encoding="utf-8")
    try:
        register(sock, reader)
    except (ConnectionError, EOFError, KeyboardInterrupt):
        sock.close()
        return

    leaving = threading.Event()
    threading.Thread(target=receive, args=(reader, leaving), daemon=True).start()

    try:
        while True:
            message = input().strip()
            if not message:
                continue
            if message == "/exit":
                break
            send_line(sock, message)
    except (EOFError, KeyboardInterrupt):
        pass

    leaving.set()
    try:
        send_line(sock, "/exit")
    except OSError:
        pass
    sock.close()
    print("Вы вышли из чата")


if __name__ == "__main__":
    main()

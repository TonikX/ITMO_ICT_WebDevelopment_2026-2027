"""Задание 4: универсальный клиент TCP-чата"""
import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5004
ENCODING = "utf-8"

def receive_messages(connection):
    try:
        reader = connection.makefile("r", encoding=ENCODING, newline="\n")
        for line in reader:
            print(line.rstrip("\r\n"))
    except (OSError, UnicodeError):
        pass
    finally:
        print("\nСоединение с чатом закрыто.")

def main():
    username = input("Введите ваше имя в чате: ").strip()
    if not username:
        print("Имя не должно быть пустым.")
        return

    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((SERVER_HOST, SERVER_PORT))
    except ConnectionRefusedError:
        print("Сервер не запущен.")
        return
    except OSError as error:
        print(f"Не удалось подключиться: {error}")
        return

    receiver = threading.Thread(target=receive_messages, args=(connection,), daemon=True)
    receiver.start()

    try:
        connection.sendall((username.replace("\n", "")[:24] + "\n").encode(ENCODING))
        print("Вы в чате. Напишите сообщение и нажмите Enter. Выход: /quit")
        while True:
            message = input()
            connection.sendall((message + "\n").encode(ENCODING))
            if message.strip().lower() == "/quit":
                break
    except (EOFError, KeyboardInterrupt):
        try:
            connection.sendall(b"/quit\n")
        except OSError:
            pass
    except OSError:
        print("Соединение потеряно.")
    finally:
        connection.close()

if __name__ == "__main__":
    main()

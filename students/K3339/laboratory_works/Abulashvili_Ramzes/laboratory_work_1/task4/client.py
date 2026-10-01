import socket
import threading

HOST = "127.0.0.1"
PORT = 5004


def receive_messages(connection, connected):
    try:
        with connection.makefile("r", encoding="utf-8", newline="\n") as reader:
            for line in reader:
                print("\n" + line.rstrip("\r\n"))
    except (OSError, UnicodeError):
        pass
    finally:
        connected.clear()
        print("\nСоединение закрыто. Нажмите Enter для выхода.")


def main():
    name = input("Ваше имя: ").strip()
    if not name:
        print("Введите имя.")
        return
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.connect((HOST, PORT))
        connection.sendall((name + "\n").encode("utf-8"))
        connected = threading.Event()
        connected.set()
        receiver = threading.Thread(target=receive_messages, args=(connection, connected), daemon=True)
        receiver.start()
        print("Вы вошли в чат. Для выхода введите /exit.")
        try:
            while connected.is_set():
                message = input("> ")
                if not connected.is_set():
                    break
                connection.sendall((message + "\n").encode("utf-8"))
                if message == "/exit":
                    break
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из чата.")
        finally:
            connected.clear()
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            receiver.join(timeout=1)


if __name__ == "__main__":
    try:
        main()
    except (OSError, EOFError, KeyboardInterrupt) as error:
        print(f"Работа клиента завершена: {error}")

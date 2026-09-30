import socket
import threading


SERVER_ADDRESS = ("127.0.0.1", 5002)


def receive_messages(client_socket: socket.socket) -> None:
    try:
        reader = client_socket.makefile("r", encoding="utf-8")
        for line in reader:
            print(f"\r{line.rstrip()}\n> ", end="", flush=True)
    except (ConnectionError, OSError, UnicodeError):
        pass


def main() -> None:
    username = input("Введите имя: ").strip()
    while not username:
        username = input("Имя не может быть пустым. Введите имя: ").strip()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(SERVER_ADDRESS)
        client_socket.sendall(f"{username}\n".encode("utf-8"))

        receiver = threading.Thread(
            target=receive_messages,
            args=(client_socket,),
            daemon=True,
        )
        receiver.start()

        try:
            while True:
                message = input("> ")
                client_socket.sendall(f"{message}\n".encode("utf-8"))
                if message == "/exit":
                    break
        except (EOFError, KeyboardInterrupt, OSError):
            try:
                client_socket.sendall(b"/exit\n")
            except OSError:
                pass

        receiver.join(timeout=1)

    print("Вы вышли из чата")


if __name__ == "__main__":
    main()

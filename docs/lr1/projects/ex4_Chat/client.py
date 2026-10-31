import socket
import threading


HOST = "127.0.0.1"
PORT = 5000


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                break

            print(f"\n{message}")
            print("> ", end="", flush=True)

        except (ConnectionResetError, ConnectionAbortedError, OSError):
            break


def start_client():
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client_socket.connect(
        (HOST, PORT)
    )

    print("=== TCP CHAT CLIENT ===")

    username = input("Введите ваше имя: ")

    client_socket.send(
        username.encode("utf-8")
    )

    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,)
    )

    receive_thread.daemon = True
    receive_thread.start()

    print("Вы подключены к чату.")
    print("Все сообщения получают все пользователи.")
    print("Для выхода: /exit")

    while True:

        text = input("> ")

        if text == "/exit":
            client_socket.send(
                "/exit".encode("utf-8")
            )
            client_socket.close()
            break

        if not text:
            continue

        client_socket.send(
            text.encode("utf-8")
        )


if __name__ == "__main__":
    start_client()
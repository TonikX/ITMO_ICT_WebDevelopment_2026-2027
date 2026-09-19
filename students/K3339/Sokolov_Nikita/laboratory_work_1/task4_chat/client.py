import socket
import threading

HOST = "127.0.0.1"
PORT = 8084
BUFFER_SIZE = 1024


def receive_messages(sock: socket.socket, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            data = sock.recv(BUFFER_SIZE)
        except OSError:
            break
        if not data:
            print("\nСоединение закрыто сервером.")
            stop_event.set()
            break
        print(data.decode("utf-8"), end="")


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        stop_event = threading.Event()

        receiver = threading.Thread(
            target=receive_messages,
            args=(client, stop_event),
            daemon=True,
        )
        receiver.start()

        try:
            while not stop_event.is_set():
                line = input()
                if stop_event.is_set():
                    break
                client.sendall((line + "\n").encode("utf-8"))
                if line.strip() == "/exit":
                    break
        except (EOFError, KeyboardInterrupt):
            try:
                client.sendall(b"/exit\n")
            except OSError:
                pass
        finally:
            stop_event.set()


if __name__ == "__main__":
    main()

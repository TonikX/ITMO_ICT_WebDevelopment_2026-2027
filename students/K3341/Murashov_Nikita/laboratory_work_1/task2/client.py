"""TCP-клиент задания 2: запрашивает гипотенузу у сервера."""

import socket

HOST = "127.0.0.1"
PORT = 11002


def main() -> None:
    """Читает катеты с клавиатуры и печатает ответ сервера.

    Args:
        None.

    Returns:
        None.
    """
    a = input("Катет a: ").strip()
    b = input("Катет b: ").strip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(f"{a} {b}".encode("utf-8"))
        print(sock.recv(1024).decode("utf-8", errors="replace"))


if __name__ == "__main__":
    main()

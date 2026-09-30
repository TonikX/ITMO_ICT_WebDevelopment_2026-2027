"""UDP-сервер задания 1.

Принимает датаграмму ``Hello, server`` и отвечает ``Hello, client``.
"""

import socket

HOST = "127.0.0.1"
PORT = 11001


def main() -> None:
    """Запускает UDP-сервер.

    Args:
        None.

    Returns:
        None. Работает бесконечно, отвечая каждому отправителю.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, PORT))
        print(f"UDP сервер: {HOST}:{PORT}")
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"{addr}: {data.decode('utf-8', errors='replace')}")
            sock.sendto(b"Hello, client", addr)


if __name__ == "__main__":
    main()

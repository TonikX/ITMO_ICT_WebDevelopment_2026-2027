import socket

HOST, PORT = "127.0.0.1", 5001


def run_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(5)

        client.sendto(b"Hello, server", (HOST, PORT))

        data, _ = client.recvfrom(4096)
        print("Сообщение сервера:", data.decode())


if __name__ == "__main__":
    run_client()

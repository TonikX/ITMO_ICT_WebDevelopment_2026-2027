import socket

HOST, PORT = "127.0.0.1", 5001


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((HOST, PORT))
        print(f"UDP-сервер запущен")

        while True:
            data, address = server.recvfrom(4096)
            print("Сообщение клиента:", data.decode())

            server.sendto(b"Hello, client", address)


if __name__ == "__main__":
    run_server()

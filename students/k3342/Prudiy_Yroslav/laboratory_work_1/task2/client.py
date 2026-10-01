import socket

HOST, PORT = "127.0.0.1", 5001


def run_client():
    a = input("Первый катет: ")
    b = input("Второй катет: ")

    with socket.create_connection((HOST, PORT), timeout=5) as client:
        client.sendall(f"{a} {b}".encode())

        print("Гипотенуза:", client.recv(1024).decode())


if __name__ == "__main__":
    run_client()

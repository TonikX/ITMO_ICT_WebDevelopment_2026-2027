import socket
import threading


HOST = "127.0.0.1"
PORT = 5000

clients = {}

lock = threading.Lock()


def broadcast(message, sender_socket):
    with lock:
        client_sockets = list(clients.keys())

    for client_socket in client_sockets:
        if client_socket != sender_socket:
            client_socket.send(message.encode("utf-8"))


def handle_client(client_socket, address):
    try:
        username = client_socket.recv(1024).decode("utf-8")

        with lock:
            clients[client_socket] = username

        print(f"[+] {username} подключился: {address}")

        while True:
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                break

            if message == "/exit":
                break

            broadcast(
                f"{username}: {message}",
                client_socket
            )

            print(f"[ALL] {username}: {message}")

    except ConnectionResetError:
        print(f"[!] Соединение с {address} было потеряно.")

    finally:
        with lock:
            if client_socket in clients:
                username = clients[client_socket]
                del clients[client_socket]
            else:
                username = "Unknown"

        client_socket.close()

        print(f"[-] {username} отключился.")


def start_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen()

    print("=== TCP CHAT SERVER ===")
    print(f"Сервер запущен на {HOST}:{PORT}")
    print("Ожидание подключений...")

    while True:
        client_socket, address = server_socket.accept()

        print(f"[Новое подключение] {address}")

        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, address)
        )

        client_thread.start()


if __name__ == "__main__":
    start_server()
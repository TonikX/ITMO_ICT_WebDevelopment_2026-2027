import socket
import threading


HOST = "127.0.0.1"
PORT = 5004
BUFFER_SIZE = 1024

clients = {}
clients_lock = threading.Lock()


def broadcast(message, sender_socket=None):
    with clients_lock:
        recipients = list(clients)

    for client_socket in recipients:
        if client_socket is sender_socket:
            continue
        try:
            client_socket.sendall(message.encode("utf-8"))
        except OSError:
            pass


def remove_client(client_socket):
    with clients_lock:
        username = clients.pop(client_socket, None)
    if username:
        print(f"{username} disconnected")
        broadcast(f"[SERVER] {username} left the chat\n")
    try:
        client_socket.close()
    except OSError:
        pass


def handle_client(conn, addr):
    try:
        conn.sendall("Введите имя: ".encode("utf-8"))
        username = conn.recv(BUFFER_SIZE).decode("utf-8").strip()
        if not username:
            username = f"user_{addr[1]}"

        with clients_lock:
            clients[conn] = username

        print(f"{username} connected from {addr}")
        conn.sendall("Для выхода напишите /exit\n".encode("utf-8"))
        broadcast(f"[SERVER] {username} joined the chat\n", conn)

        while True:
            message = conn.recv(BUFFER_SIZE).decode("utf-8").strip()
            if not message or message == "/exit":
                break
            broadcast(f"{username}: {message}\n", conn)
    except OSError:
        pass
    finally:
        remove_client(conn)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Чат запущен: {HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True,
            )
            thread.start()


if __name__ == "__main__":
    main()

import socket
import threading

HOST, PORT = "127.0.0.1", 5001
clients = {}
lock = threading.Lock()


def broadcast(message, sender=None):
    with lock:
        recipients = list(clients)
    for client in recipients:
        if client != sender:
            try:
                client.sendall((message + "\n").encode())
            except OSError:
                pass


def handle_client(client):
    name = None
    try:
        client.sendall("Введите имя:\n".encode())
        name = client.recv(1024).decode().strip()
        with lock:
            if name in clients.values():
                client.sendall("Это имя уже занято.\n".encode())
                return
            clients[client] = name
        client.sendall("Вы вошли в чат. Для выхода: /quit\n".encode())
        broadcast(f"*** {name} вошёл в чат ***", client)
        while True:
            message = client.recv(4096).decode().strip()
            if not message or message == "/quit":
                break
            broadcast(f"{name}: {message}", client)
    except OSError:
        pass
    finally:
        with lock:
            clients.pop(client, None)
        client.close()
        if name:
            broadcast(f"*** {name} вышел из чата ***")


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Сервер чата запущен на {HOST}:{PORT}")
        while True:
            client, _ = server.accept()
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()


if __name__ == "__main__":
    run_server()

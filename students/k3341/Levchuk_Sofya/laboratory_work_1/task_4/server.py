import socket
import threading

clients = {}
lock = threading.Lock()

def broadcast(message, sender_socket=None):
    with lock:
        for client_socket in list(clients.keys()):
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(message.encode())
                except Exception:
                    client_socket.close()
                    if client_socket in clients:
                        del clients[client_socket]

def handle_client(client_socket, client_address):
    print(f"поток запущен для {client_address}")
    try:
        username = client_socket.recv(1024).decode()
        with lock:
            clients[client_socket] = username

        print(f"{client_address} представился как {username}")
        broadcast(f"{username} присоединился к чату", sender_socket = client_socket)

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode()

            if message.strip() == "/exit":
                break

            broadcast(f"[{username}]:{message}", sender_socket = client_socket)

    except Exception:
        print(f"ошибка при обработке {client_address}")

    finally:
        username = None
        with lock:
            if client_socket in clients:
                username = clients[client_socket]
                del clients[client_socket]
        if username:
            broadcast(f"{username} покинул чат")

        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 8080))
    server_socket.listen()
    print(f"чат-сервер запущен на localhost:8080")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"новое подключение: {client_address}")

        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()
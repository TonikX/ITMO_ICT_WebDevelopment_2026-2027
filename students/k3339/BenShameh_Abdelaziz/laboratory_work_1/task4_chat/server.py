import socket
import threading

HOST = "127.0.0.1"
PORT = 5003

# Shared state: maps username -> connection socket.
# Every client-handling thread reads/writes this, so we protect it with a lock.
clients = {}
clients_lock = threading.Lock()

def broadcast(message: str, exclude_username: str = None):
    """Send `message` to every connected client except `exclude_username`."""
    with clients_lock:
        for username, conn in list(clients.items()):
            if username == exclude_username:
                continue
            try:
                conn.sendall(message.encode())
            except OSError:
                pass  # that client's socket died; their own thread will clean it up

def handle_client(conn: socket.socket, addr):
    """
    Runs in its own thread, one per connected client.
    This is what lets the server serve many users AT THE SAME TIME:
    each thread blocks independently on its own conn.recv(), so one
    slow/idle client never blocks the others.
    """
    username = None
    try:
        # Protocol: the very first message a client sends is its username.
        username = conn.recv(1024).decode().strip()

        with clients_lock:
            clients[username] = conn
        print(f"[SERVER] {username} joined from {addr}")
        broadcast(f"*** {username} has joined the chat ***", exclude_username=username)

        while True:
            data = conn.recv(1024)
            if not data:
                break  # client closed the connection
            text = data.decode().strip()

            if text == "/quit":
                break

            print(f"[SERVER] {username}: {text}")
            broadcast(f"{username}: {text}", exclude_username=username)

    except (ConnectionResetError, OSError):
        pass
    finally:
        if username:
            with clients_lock:
                clients.pop(username, None)
            print(f"[SERVER] {username} left")
            broadcast(f"*** {username} has left the chat ***", exclude_username=username)
        conn.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVER] Chat server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        # A new thread per client -> server can handle many people concurrently
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    main()

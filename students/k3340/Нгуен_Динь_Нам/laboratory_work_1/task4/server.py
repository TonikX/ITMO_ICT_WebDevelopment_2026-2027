import socket
import threading

clients = {}
clients_lock = threading.Lock()

def broadcast(message, sender_socket):
    payload = (message + "\n").encode("utf-8")

    with clients_lock:
        recipients = [
            (client_socket, client_info["send_lock"])
            for client_socket, client_info in clients.items()
            if client_socket != sender_socket
        ]

    for recipient_socket, send_lock in recipients:
        try:
            with send_lock:
                recipient_socket.sendall(payload)
        except OSError:
            continue

def handle_client(client_socket, address):
    buffer = b""
    nickname = None

    try:
        while True:
            chunk = client_socket.recv(1024)

            if not chunk:
                break

            buffer += chunk

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                text = line.decode("utf-8").rstrip("\r")

                if nickname is None:
                    nickname = text.strip()

                    if not nickname:
                        client_socket.sendall(b"Nickname must not be empty.\n")
                        return

                    welcome = (
                        f"Hello, {nickname}! "
                        "You are connected to the server.\n"
                    )
                    client_socket.sendall(welcome.encode("utf-8"))

                    with clients_lock:
                        clients[client_socket] = {
                            "nickname": nickname,
                            "send_lock": threading.Lock(),
                        }

                    print(f"{nickname} connected from {address}")

                else:
                    message = f"{nickname}: {text}"
                    print(message)
                    broadcast(message, client_socket)

    except (OSError, UnicodeError) as error:
        print(f"Connection error from {address}: {error}")

    finally:
        with clients_lock:
            client_info = clients.pop(client_socket, None)

        client_socket.close()

        if client_info is not None:
            print(f"{client_info['nickname']} disconnected.")


socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket_server.bind(('localhost', 8080))
    socket_server.listen(10)
    socket_server.settimeout(1.0)
    
    print('Server is listening on port 8080...')

    while True:
        try:
            client_socket, address = socket_server.accept()
        except socket.timeout:
            continue

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, address),
            daemon=True,
        )
        thread.start()

finally:
    socket_server.close()

    with clients_lock:
        remaining_clients = list(clients)

    for client_socket in remaining_clients:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client_socket.close()
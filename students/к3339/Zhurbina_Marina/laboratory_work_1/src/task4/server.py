import socket
import threading

ADDRESS = "127.0.0.1"
PORT = 9004

members = {}
guard = threading.Lock()


def spread(text, skip):
    with guard:
        current = list(members.keys())
    broken = []
    for client in current:
        if client != skip:
            try:
                client.sendall(text.encode())
            except Exception:
                broken.append(client)
    with guard:
        for client in broken:
            client.close()
            members.pop(client, None)


def serve(client_socket, address):
    name = client_socket.recv(1024).decode()
    if not name:
        client_socket.close()
        return
    with guard:
        members[client_socket] = name
    print(f"{name} вошёл ({address})")
    spread(f"{name} зашёл в чат", client_socket)

    while True:
        try:
            text = client_socket.recv(1024).decode()
        except Exception:
            text = ""
        if not text or text == "exit":
            break
        print(f"{name}: {text}")
        spread(f"{name}: {text}", client_socket)

    with guard:
        members.pop(client_socket, None)
    client_socket.close()
    print(f"{name} вышел")
    spread(f"{name} покинул чат", client_socket)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ADDRESS, PORT))
    server.listen(5)
    print(f"Чат запущен на {ADDRESS}:{PORT}")

    while True:
        client_socket, address = server.accept()
        threading.Thread(target=serve, args=(client_socket, address)).start()


main()
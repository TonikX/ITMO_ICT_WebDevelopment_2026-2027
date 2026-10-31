import socket
import threading

HOST = "localhost"
PORT = 9004

clients = {}
clients_lock = threading.Lock()


def broadcast(message, sender):
    with clients_lock:
        for client_socket in clients:
            if client_socket is not sender:
                try:
                    client_socket.sendall(message.encode())
                except OSError:
                    pass


def handle_client(client_socket, client_address):
    reader = client_socket.makefile("r", encoding="utf-8")
    name = ""
    try:
        name = reader.readline().strip()
        if not name:
            return
        with clients_lock:
            clients[client_socket] = name
        print(f"{name} вошёл в чат {client_address}")

        for line in reader:
            message = line.strip()
            if message == "/exit":
                break
            print(f"{name}: {message}")
            broadcast(f"{name}: {message}\n", client_socket)
    except OSError:
        pass
    finally:
        with clients_lock:
            clients.pop(client_socket, None)
        reader.close()
        client_socket.close()
        if name:
            print(f"{name} вышел из чата")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Сервер чата запущен на {HOST}:{PORT}")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True).start()
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()

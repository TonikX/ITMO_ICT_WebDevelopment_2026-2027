import socket
import threading

HOST = "127.0.0.1"
PORT = 8084

clients = {}
lock = threading.Lock()


def broadcast(text, sender=None):
    with lock:
        for conn in clients:
            if conn is not sender:
                try:
                    conn.sendall(text.encode())
                except OSError:
                    pass


def handle_client(conn, address):
    name = None
    try:
        conn.sendall("Введите имя:\n".encode())
        while name is None:
            data = conn.recv(1024)
            if not data:
                return
            new_name = data.decode().strip()
            with lock:
                if new_name not in clients.values():
                    clients[conn] = new_name
                    name = new_name
            if name is None:
                conn.sendall("Имя занято, введите другое:\n".encode())

        print(f"{address} вошёл как {name}")
        conn.sendall("Вы в чате. Для выхода введите /quit\n".encode())
        broadcast(f"{name} вошёл в чат\n", conn)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = f"{name}: {data.decode().strip()}"
            print(message)
            broadcast(message + "\n", conn)
    except OSError:
        pass
    finally:
        with lock:
            clients.pop(conn, None)
        conn.close()
        if name is not None:
            print(f"{name} вышел")
            broadcast(f"{name} вышел из чата\n")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Сервер чата запущен на {HOST}:{PORT}")

while True:
    conn, address = server.accept()
    threading.Thread(target=handle_client, args=(conn, address), daemon=True).start()

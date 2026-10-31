import socket
import threading

ADDRESS = ("localhost", 5004)

users = {}
lock = threading.Lock()


def send_all(text, sender=None):
    with lock:
        receivers = [conn for conn in users if conn is not sender]

    for conn in receivers:
        try:
            conn.sendall((text + "\n").encode())
        except OSError:
            pass


def serve(conn, address):
    name = conn.recv(1024).decode().strip()
    with lock:
        users[conn] = name
    print(f"Подключение: {name} {address}")
    send_all(f"{name} присоединяется к чату", conn)

    try:
        while True:
            text = conn.recv(1024).decode().strip()
            if not text or text == "/exit":
                break
            print(f"{name}: {text}")
            send_all(f"{name}: {text}", conn)
    except ConnectionError:
        pass
    finally:
        with lock:
            del users[conn]
        conn.close()
        print(f"Отключение: {name}")
        send_all(f"{name} покидает чат")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(ADDRESS)
    sock.listen()
    print("Чат запущен на", ADDRESS)

    while True:
        conn, address = sock.accept()
        threading.Thread(target=serve, args=(conn, address), daemon=True).start()

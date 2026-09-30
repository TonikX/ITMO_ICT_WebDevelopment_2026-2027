import socket
import threading

HOST, PORT = "localhost", 8080

clients = {}
clients_lock = threading.Lock()


def send_line(conn, text):
    try:
        conn.sendall((text + "\n").encode("utf-8"))
    except OSError:
        pass


def broadcast(text, exclude=None):
    """Разослать сообщение всем, кроме exclude (отправителя)."""
    with clients_lock:
        targets = [c for nick, c in clients.items() if nick != exclude]
    for c in targets:
        send_line(c, text)


def handle_client(conn, addr):
    nickname = None
    try:
        reader = conn.makefile("r", encoding="utf-8")
        send_line(conn, "Введите ваш ник:")

        while True:
            line = reader.readline()
            if not line:
                return
            nick = line.strip()
            with clients_lock:
                if nick and not nick.startswith("/") and nick not in clients:
                    clients[nick] = conn
                    nickname = nick
                    break
            send_line(conn, "Ник пустой, начинается с '/' или уже занят. Другой ник:")

        print(f"{nickname} подключился ({addr})")
        send_line(conn, f"Добро пожаловать, {nickname}! Для выхода введите /exit")
        broadcast(f"*** {nickname} вошёл в чат ***", exclude=nickname)

        for line in reader:
            text = line.strip()
            if text == "/exit":
                break
            if text:
                broadcast(f"[{nickname}]: {text}", exclude=nickname)
    except (ConnectionError, OSError):
        pass
    finally:
        if nickname:
            with clients_lock:
                clients.pop(nickname, None)
            broadcast(f"*** {nickname} покинул чат ***")
            print(f"{nickname} отключился")
        conn.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Чат-сервер запущен на {HOST}:{PORT}")

try:
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
except KeyboardInterrupt:
    print("\nСервер остановлен")
finally:
    server_socket.close()

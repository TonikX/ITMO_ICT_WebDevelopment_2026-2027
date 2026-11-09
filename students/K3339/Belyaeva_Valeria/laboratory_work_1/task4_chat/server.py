import socket
import threading

clients = {} # {socket: username}

def handle_client(conn, addr):
    # Первый пакет - имя пользователя
    name = conn.recv(1024).decode('utf-8')
    clients[conn] = name
    broadcast(f"--- {name} присоединился к чату ---", conn)

    while True:
        try:
            msg = conn.recv(1024).decode('utf-8')
            if not msg: break
            broadcast(f"[{name}]: {msg}", conn)
        except:
            break

    del clients[conn]
    conn.close()
    broadcast(f"--- {name} покинул чат ---", None)

def broadcast(message, sender_conn):
    # list() - копия, чтобы другой поток не изменил словарь во время обхода
    for c in list(clients):
        if c != sender_conn:
            try:
                c.send(message.encode('utf-8'))
            except:
                pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Позволяет сразу перезапускать сервер на том же порту
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 8084))
server.listen(5)
print("Чат-сервер запущен...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()

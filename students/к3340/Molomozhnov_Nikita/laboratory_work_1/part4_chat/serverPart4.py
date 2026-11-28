import socket
import threading

clients = []
lock = threading.Lock()

def broadcast(msg, sender=None):
    with lock:
        for client in clients:
            if client != sender:
                try:
                    client.send(msg.encode('utf-8', errors='ignore'))
                except:
                    pass

def handle(sock):
    sock.send("Введите имя: ".encode())
    name = sock.recv(1024).decode('utf-8', errors='ignore').strip()
    with lock:
        clients.append(sock)
    broadcast(f" {name} в чате \n", sock)
    print(f"{name} подключился")

    while True:
        data = sock.recv(1024)
        if not data:
            break
        msg = data.decode('utf-8', errors='ignore').strip()
        if msg == '/quit':
            break
        broadcast(f"[{name}]: {msg}\n", sock)

    with lock:
        clients.remove(sock)
    broadcast(f" {name} вышел \n")
    print(f"{name} отключился")
    sock.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 5013))
server.listen(10)
print("Сервер запущен")

while True:
    sock, _ = server.accept()
    threading.Thread(target=handle, args=(sock,), daemon=True).start()
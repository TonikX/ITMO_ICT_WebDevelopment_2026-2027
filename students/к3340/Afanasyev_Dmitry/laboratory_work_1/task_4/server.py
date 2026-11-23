import socket
import threading

CHAT = []
LOCK = threading.Lock()


def chat(client):
    try:
        with client.makefile('r', encoding='utf-8') as messages:
            name = messages.readline().strip()
            if not name:
                return
            CHAT.append(client)
            for text in messages:
                if text.strip() == '/exit':
                    break
                with LOCK:
                    for user in CHAT.copy():
                        if user != client:
                            try:
                                user.sendall(f'{name}: {text}'.encode())
                            except OSError:
                                pass
    except OSError:
        pass
    finally:
        if client in CHAT:
            CHAT.remove(client)
        client.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 9999))
server.listen(5)
print("Чат запущен")

while True:
    client, addr = server.accept()
    threading.Thread(target=chat, args=(client,), daemon=True).start()

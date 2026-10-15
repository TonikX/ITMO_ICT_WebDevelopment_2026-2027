import socket
import threading

HOST = 'localhost'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

lock = threading.Lock()

# Словарь {socket: username} — хранит активных пользователей
clients = {}

print(f"Сервер запущен на {HOST}:{PORT}")

def broadcast(message, exclude=None):
    """Рассылает сообщение всем, кроме отправителя."""
    with lock:
        for client in list(clients.keys()):
            if client is exclude:
                continue
            try:
                client.sendall(message.encode('utf-8'))
            except OSError:
                client.close()
                clients.pop(client, None)

def handle_client(client_socket, address):
    try:
        nickname = client_socket.recv(1024).decode('utf-8').strip()

        with lock:
            clients[client_socket] = nickname

        print(f"[+] {nickname} подключился ({address})")
        broadcast(f"*** {nickname} присоединился к чату ***", exclude=client_socket)

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            message = data.decode('utf-8').strip()

            # Команда выхода
            if message.lower() == '/exit':
                break

            print(f"{nickname}: {message}")
            broadcast(f"{nickname}: {message}", exclude=client_socket)
    except:
        pass
    finally:
        with lock:
            clients.pop(client_socket, None)
        try:
            client_socket.close()
        except:
            pass
        print(f"[-] {nickname if 'nickname' in dir() else address} отключился")
        broadcast(f"*** {nickname} покинул чат ***")


while True:
    client_socket, address = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, address), daemon=True)
    thread.start()
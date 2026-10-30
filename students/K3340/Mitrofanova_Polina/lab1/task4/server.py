import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

clients = {}  # {socket: nickname}

def broadcast(message, sender_socket=None):
    """Рассылка сообщения всем клиентам, кроме отправителя."""
    for client in list(clients.keys()):
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove_client(client)

def remove_client(client_socket):
    """Удаление отключенного клиента."""
    if client_socket in clients:
        nickname = clients[client_socket]
        del clients[client_socket]
        client_socket.close()
        print(f"[{nickname}] отключился.")
        broadcast(f"--- {nickname} покинул чат ---")

def handle_client(client_socket):
    """Обработка отдельного клиента в своем потоке."""
    try:
        client_socket.send("NICK_REQUEST".encode('utf-8'))
        nickname = client_socket.recv(1024).decode('utf-8').strip()
        
        clients[client_socket] = nickname
        print(f"Пользователь [{nickname}] подключился.")
        broadcast(f"--- {nickname} вошёл в чат ---", client_socket)
        
        client_socket.send("Добро пожаловать в чат! Для выхода введите /exit\n".encode('utf-8'))

        while True:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg or msg.strip() == '/exit':
                break
            broadcast(f"{nickname}: {msg}", client_socket)
    except ConnectionResetError:
        pass
    finally:
        remove_client(client_socket)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Чат-сервер запущен на {HOST}:{PORT}...")

    while True:
        client_socket, _ = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()
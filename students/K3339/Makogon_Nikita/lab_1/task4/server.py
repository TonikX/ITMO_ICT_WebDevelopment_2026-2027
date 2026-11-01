import socket
import threading

HOST = '127.0.0.1'
PORT = 8084

clients = []
clients_lock = threading.Lock()

def broadcast(message, exclude_socket=None):
    with clients_lock:
        for client in clients:
            if client != exclude_socket:
                try:
                    client.sendall(message)
                except Exception:
                    pass

def handle_client(client_socket, client_address):
    print(f"[ПОДКЛЮЧЕНИЕ] Установлено соединение с {client_address}")
    try:
        username_bytes = client_socket.recv(1024)
        if not username_bytes:
            return
        username = username_bytes.decode('utf-8').strip()
        if not username:
            username = f"User_{client_address[1]}"

        print(f"[ПОЛЬЗОВАТЕЛЬ] {client_address} зарегистрирован как '{username}'")
        
        join_msg = f"[СЕРВЕР]: {username} присоединился к чату.\n"
        broadcast(join_msg.encode('utf-8'), exclude_socket=client_socket)

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            message_text = data.decode('utf-8').strip()
            if message_text.lower() == 'exit':
                break

            formatted_msg = f"[{username}]: {message_text}\n"
            print(f"[{username}]: {message_text}")
            broadcast(formatted_msg.encode('utf-8'), exclude_socket=client_socket)

    except ConnectionResetError:
        pass
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        
        left_msg = f"[СЕРВЕР]: {username if 'username' in locals() else 'Кто-то'} покинул чат.\n"
        print(f"[ОТКЛЮЧЕНИЕ] {client_address} отключился.")
        broadcast(left_msg.encode('utf-8'))

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[ЧАТ СЕРВЕР] Запущен на {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            with clients_lock:
                clients.append(client_socket)
            
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[ЧАТ СЕРВЕР] Выключается...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_server()
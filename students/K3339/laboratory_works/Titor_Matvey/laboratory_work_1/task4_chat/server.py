import socket
import threading

HOST = 'localhost'
PORT = 9002

clients = {}
clients_lock = threading.Lock()


def broadcast(message, sender_conn=None):
    with clients_lock:
        recipients = [conn for conn in clients if conn != sender_conn]
    for conn in recipients:
        try:
            conn.sendall(message.encode())
        except OSError:
            remove_client(conn)


def remove_client(conn):
    with clients_lock:
        name = clients.pop(conn, None)
    if name:
        print(f'[{name} покинул чат]')
    conn.close()


def handle_client(conn, address):
    username = conn.recv(1024).decode()
    if not username:
        remove_client(conn)
        return

    with clients_lock:
        clients[conn] = username
    print(f'[{username} подключился из {address}]')
    broadcast(f'* {username} вошел в чат', conn)

    while True:
        try:
            data = conn.recv(1024)
        except ConnectionResetError:
            break
        if not data:
            break
        text = data.decode().strip()
        if text == '/exit':
            break
        if text:
            print(f'{username}: {text}')
            broadcast(f'{username}: {text}', conn)

    remove_client(conn)
    broadcast(f'* {username} покинул чат')


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'Сервер чата запущен на {HOST}:{PORT}. Ожидание пользователей...')

while True:
    conn, address = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, address), daemon=True).start()

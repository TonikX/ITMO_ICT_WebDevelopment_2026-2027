import socket
import threading

HOST = '127.0.0.1'
PORT = 8084

clients = {}  # сокет-ник
lock = threading.Lock()


def broadcast(message, sender_socket):
    with lock:
        recipients = list(clients.keys())
    to_remove = []
    for client_socket in recipients:
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message.encode())
            except Exception:
                to_remove.append(client_socket)
    with lock:
        for sock in to_remove:
            sock.close()
            clients.pop(sock, None)


def handle_client(client_socket, address):
    nickname = client_socket.recv(1024).decode()
    if not nickname:
        client_socket.close()
        return
    with lock:
        clients[client_socket] = nickname
    print(f'{nickname} подключился ({address})')
    broadcast(f'{nickname} вошёл в чат', client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode()
        except Exception:
            message = ''
        if not message or message == 'exit':
            break
        print(f'{nickname}: {message}')
        broadcast(f'{nickname}: {message}', client_socket)

    with lock:
        clients.pop(client_socket, None)
    client_socket.close()
    print(f'{nickname} вышел из чата')
    broadcast(f'{nickname} вышел из чата', client_socket)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f'Сервер запущен по адресу {HOST}:{PORT}...')

    while True:
        client_socket, address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.start()


if __name__ == '__main__':
    main()
import socket
import threading

tcp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# привяжем сокет к адресу и порту
tcp_server_sock.bind(("localhost", 8080))
tcp_server_sock.listen()
print("Сервер запущен.....")

# словарь, где сервер будет хранить пользователей: соединение -> имя
users = {}


def broadcast(message, conn):
    for user_conn in list(users.keys()):
        if user_conn != conn:
            user_conn.send(message.encode())


def handle_client(conn):
    # первое сообщение от клиента - его имя
    users[conn] = conn.recv(1024).decode()
    message = f"Пользователь {users[conn]} присоединился к чату"
    broadcast(message, conn)
    print(message)

    while True:
        data = conn.recv(1024)
        # пустые данные значит клиент закрыл соединение, '/exit' значит вышел сам
        if not data or data.decode() == '/exit':
            message = f'Пользователь {users[conn]} покинул чат'
            broadcast(message, conn)
            print(message)
            del users[conn]
            conn.close()
            break
        message = f"({users[conn]}): {data.decode()}"
        broadcast(message, conn)
        print(message)


while True:
    # ожидание новых подключений
    conn, addr = tcp_server_sock.accept()
    # для каждого клиента отдельный поток
    thread = threading.Thread(target=handle_client, args=(conn,), daemon=True)
    thread.start()
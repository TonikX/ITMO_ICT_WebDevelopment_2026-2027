import socket
import threading

host = 'localhost'
port = 8083

clients = {}

def sendMessage(message, sender_connection):
    for connection in list(clients):
        if connection is sender_connection:
            continue
        try:
            connection.sendall(message.encode())
        except OSError:
            remove_client(connection)


def remove_client(connection):
    name = clients.pop(connection, None)
    if name is None:
        return
    print(f"[{name} отключился]")
    sendMessage(f"[{name} отключился]\n", connection)
    try:
        connection.close()
    except OSError:
        pass


def handle_client(connection, address):
    try:
        connection.sendall("Введите имя: ".encode())
        name = connection.recv(1024).decode().strip()
        clients[connection] = name
        print(f"[{name} подключился]")
        sendMessage(f"[{name} подключился]\n", connection)
        connection.sendall(
            f"{name}, добро пожаловать! Напишите \\exit для выхода. Пишите сообщение в пустой строке и оно будет видно в чате\n".encode()
        )

        while True:
            data = connection.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            if not message:
                continue
            if message == r"\exit":
                break
            print(f"[{name} - {message}]")
            sendMessage(f"[{name}]: {message}\n", connection)
    except OSError:
        pass
    finally:
        remove_client(connection)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()
print(f"[Сервер запущен на порту - {port}]")

while True:
    connection, address = server.accept()
    threading.Thread(target=handle_client, args=(connection, address), daemon=True).start()
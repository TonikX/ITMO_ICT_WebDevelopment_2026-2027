import threading
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(("localhost", 8000))
server_socket.listen(5)
print("Сервер запущен на порту 8000...")
clients = {}

def thread_clients(client_connection, client_address):
    print(f"Подключился клиент: {client_address}")

    name = client_connection.recv(1024).decode()
    print(f"Подключился пользователь: {name}")
    clients[name] = client_connection
    while True:
        try:
            message = client_connection.recv(1024).decode()

            if not message:
                break
        except ConnectionResetError:
            break

        print(f"{name}: {message}")
        for username, client in clients.items():
            if client != client_connection:
                client.sendall(f"{name}: {message}".encode())

    if name in clients:
        del clients[name]
    client_connection.close()
    print(f"Пользователь {name} отключился")



while True:
    client_connection, client_address = server_socket.accept()
    ## создаем новый поток в котором будет выполняться функция передаем функции 2 аругмента и запуск потока
    thread = threading.Thread(
        target=thread_clients,
        args=(client_connection, client_address)
    )
    thread.start()

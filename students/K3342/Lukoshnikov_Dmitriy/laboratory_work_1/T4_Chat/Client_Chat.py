import socket
import sys
import threading

host = 'localhost'
port = 8083

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Сервер закрыл соединение.")
                break
            print(data.decode(), end='')
        except OSError:
            break
    sock.close()
    sys.exit(0)


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

print(client_socket.recv(1024).decode(), end='')
name = input()
try:
    client_socket.sendall(name.encode())
except OSError:
    print("Сервер вылетел, попробуйте позже")
    sys.exit(0)

threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

while True:
    message = input()
    if not message:
        continue
    try:
        client_socket.sendall(message.encode())
    except OSError:
        print("Сервер вылетел, попробуйте позже")
        sys.exit(0)
    if message == r"\exit":
        print("Вы вышли из чата")
        client_socket.close()
        sys.exit(0)
    print(f"Вы[{name}] отправили сообщение в чат - {message}")
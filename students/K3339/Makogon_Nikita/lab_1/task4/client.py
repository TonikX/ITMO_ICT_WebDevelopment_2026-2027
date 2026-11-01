import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 8084

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[Соединение с сервером закрыто]")
                break
            sys.stdout.write('\r\033[K')
            sys.stdout.write(data.decode('utf-8'))
            sys.stdout.write("Вы: ")
            sys.stdout.flush()
        except Exception:
            print("\n[Ошибка связи с сервером]")
            break

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Не удалось подключиться к серверу {HOST}:{PORT}.")
        return

    username = input("Введите ваше имя для входа в чат: ").strip()
    if not username:
        username = "Guest"
    client_socket.sendall(username.encode('utf-8'))

    print("\n[УСПЕХ] Вы в чате! Для выхода введите 'exit'.\n")

    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    recv_thread.daemon = True
    recv_thread.start()

    try:
        while True:
            message = input("Вы: ")
            if not message.strip():
                continue
            
            client_socket.sendall(message.encode('utf-8'))
            if message.lower() == 'exit':
                break
    except KeyboardInterrupt:
        print("\nВыход из чата...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    run_client()
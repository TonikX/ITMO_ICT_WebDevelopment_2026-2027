import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 12345

def receive_messages(sock):
    """Фоновый поток для приёма сообщений от сервера."""
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if not msg:
                break
            if msg == "NICK_REQUEST":
                nickname = input("Введите ваш никнейм: ")
                sock.send(nickname.encode('utf-8'))
            else:
                print(f"\n{msg}\n> ", end="")
        except:
            print("\nСоединение с сервером прервано.")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Сервер недоступен.")
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        try:
            message = input("> ")
            if message.strip() == '/exit':
                client.send('/exit'.encode('utf-8'))
                break
            if message.strip():
                client.send(message.encode('utf-8'))
        except (KeyboardInterrupt, EOFError):
            client.send('/exit'.encode('utf-8'))
            break

    client.close()
    print("Вы вышли из чата.")

if __name__ == "__main__":
    main()
import socket
import threading

ADDRESS = "127.0.0.1"
PORT = 9004


def listener(sock):
    while True:
        try:
            text = sock.recv(1024).decode()
        except Exception:
            break
        if not text:
            break
        print(text)


def main():
    nick = input("Ваш ник: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ADDRESS, PORT))
    sock.sendall(nick.encode())
    threading.Thread(target=listener, args=(sock,), daemon=True).start()
    print("Вы в чате. Для выхода введите 'exit'")

    while True:
        text = input()
        sock.sendall(text.encode())
        if text == "exit":
            break

    sock.close()


main()
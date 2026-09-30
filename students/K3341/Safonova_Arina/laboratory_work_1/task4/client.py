import socket
import threading


def receive_messages(client_socket):
    try:
        with client_socket.makefile('r', encoding='utf-8') as stream:
            for line in stream:
                print(line.rstrip())
    except (OSError, UnicodeError):
        pass


name = input('Ваше имя: ').strip()
if not name:
    raise SystemExit('Имя не должно быть пустым')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect(('127.0.0.1', 8004))
    client_socket.sendall((name + '\n').encode('utf-8'))
    print('Выход: /exit')
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    try:
        while True:
            message = input()
            client_socket.sendall((message + '\n').encode('utf-8'))
            if message == '/exit':
                break
    except (EOFError, KeyboardInterrupt, OSError):
        pass
    finally:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

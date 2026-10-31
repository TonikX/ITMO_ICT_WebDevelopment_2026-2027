"""Задание 4. Многопользовательский чат
Один и тот же скрипт запускают все пользователи в своих терминалах
"""

import socket
import threading

SERVER = ('127.0.0.1', 9097)
LEAVE_COMMAND = '/quit'


def listener(reader):
    for line in reader:
        print(f'\r  {line.strip()}\n> ', end='', flush=True)
    print('\nСвязь с сервером прервана.')


def main():
    nickname = input('Введите имя: ').strip()
    if not nickname:
        print('Имя не может быть пустым.')
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(SERVER)
        client.sendall((nickname + '\n').encode('utf-8'))

        threading.Thread(
            target=listener,
            args=(client.makefile('r', encoding='utf-8'),),
            daemon=True,
        ).start()

        print(f'Вы в чате {SERVER[0]}:{SERVER[1]}. Команда {LEAVE_COMMAND} — выход.')
        while True:
            text = input('> ').strip()

            if text == LEAVE_COMMAND:
                client.sendall((LEAVE_COMMAND + '\n').encode('utf-8'))
                break
            if text:
                client.sendall((text + '\n').encode('utf-8'))

    print('Вы вышли из чата.')


if __name__ == '__main__':
    main()

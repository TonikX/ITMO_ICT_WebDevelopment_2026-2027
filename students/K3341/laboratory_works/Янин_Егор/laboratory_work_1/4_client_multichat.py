import socket
import threading

HOST = 'localhost'
PORT = 9090


def receive_message_loop(reader):
    for message in reader:
        print(message, end='')


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        reader = client_socket.makefile('r', encoding='utf-8')

        prompt = reader.readline()
        if not prompt:
            print('Server closed the connection.')
            return
        print(prompt, end='')
        username = input().strip()
        client_socket.sendall(f'{username}\n'.encode('utf-8'))

        response = reader.readline()
        if not response:
            print('Server closed the connection.')
            return
        print(response, end='')
        if response.startswith('Username is empty or already in use.'):
            return

        receive_thread = threading.Thread(
            target=receive_message_loop,
            args=(reader,),
            daemon=True,
        )
        receive_thread.start()

        try:
            while True:
                message = input()
                client_socket.sendall(f'{message}\n'.encode('utf-8'))
                if message.lower() == 'exit':
                    break
        except (EOFError, OSError):
            pass

        receive_thread.join()
        reader.close()


if __name__ == '__main__':
    main()
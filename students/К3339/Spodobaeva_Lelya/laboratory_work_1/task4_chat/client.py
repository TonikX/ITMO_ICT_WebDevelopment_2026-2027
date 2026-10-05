import socket
import threading


HOST = "127.0.0.1"
PORT = 5004
BUFFER_SIZE = 1024


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode("utf-8")
            if not message:
                break
            print(message, end="")
        except OSError:
            break


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        receiver = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
        receiver.start()

        while True:
            message = input()
            client_socket.sendall(message.encode("utf-8"))
            if message == "/exit":
                break


if __name__ == "__main__":
    main()

import socket
import threading

HOST, PORT = "127.0.0.1", 5001

def receive_messages(client):
    try:
        while data := client.recv(4096):
            print(data.decode("utf-8"), end="")
    except OSError:
        pass


def run_client():
    with socket.create_connection((HOST, PORT)) as client:
        threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
        try:
            while True:
                message = input()
                client.sendall((message + "\n").encode("utf-8"))
                if message == "/quit":
                    break
        except (EOFError, KeyboardInterrupt):
            client.sendall(b"/quit\n")


if __name__ == "__main__":
    run_client()

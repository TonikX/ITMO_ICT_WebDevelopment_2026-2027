import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5003

def listen_for_messages(sock: socket.socket):
    """
    Runs in a background thread so the client can RECEIVE messages
    at any moment, without blocking the main thread that's waiting
    for the user to type something.
    """
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break
        if not data:
            print("\n[CLIENT] Disconnected from server.")
            break
        print(f"\n{data.decode()}\nYou: ", end="", flush=True)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    username = input("Choose a username: ").strip()
    client_socket.sendall(username.encode())

    receiver = threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True)
    receiver.start()

    print("Connected. Type a message and press Enter. Type /quit to leave.")
    while True:
        text = input("You: ")
        client_socket.sendall(text.encode())
        if text.strip() == "/quit":
            break

    client_socket.close()

if __name__ == "__main__":
    main()

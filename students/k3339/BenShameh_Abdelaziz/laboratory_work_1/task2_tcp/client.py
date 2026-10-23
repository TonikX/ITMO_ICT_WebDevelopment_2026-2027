import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect() performs the TCP three-way handshake with the server
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"[CLIENT] Connected to {SERVER_HOST}:{SERVER_PORT}")

    base = float(input("Enter base of the parallelogram: "))
    height = float(input("Enter height of the parallelogram: "))

    message = f"{base},{height}"
    client_socket.sendall(message.encode())
    print(f"[CLIENT] Sent: {message}")

    data = client_socket.recv(1024).decode()
    print(f"[CLIENT] Area received from server: {data}")

    client_socket.close()

if __name__ == "__main__":
    main()

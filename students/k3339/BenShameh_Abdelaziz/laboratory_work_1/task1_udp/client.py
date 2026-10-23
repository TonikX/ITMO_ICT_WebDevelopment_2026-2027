import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = "Hello, server"

    client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
    print(f"[CLIENT] Sent: {message}")

    data, server_address = client_socket.recvfrom(1024)
    print(f"[CLIENT] Received from {server_address}: {data.decode()}")

    client_socket.close()

if __name__ == "__main__":
    main()

import socket


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        print(f"UDP server is listening on {HOST}:{PORT}")

        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        message = data.decode("utf-8")
        print(f"Received from client: {message}")

        response = "Hello, client"
        server_socket.sendto(response.encode("utf-8"), client_address)
        print(f"Sent to client: {response}")


if __name__ == "__main__":
    main()

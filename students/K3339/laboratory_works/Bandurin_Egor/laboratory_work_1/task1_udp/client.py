import socket


SERVER_ADDRESS = ("127.0.0.1", 5000)
BUFFER_SIZE = 1024


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        message = "Hello, server"
        client_socket.sendto(message.encode("utf-8"), SERVER_ADDRESS)
        print(f"Sent to server: {message}")

        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        response = data.decode("utf-8")
        print(f"Received from server: {response}")


if __name__ == "__main__":
    main()

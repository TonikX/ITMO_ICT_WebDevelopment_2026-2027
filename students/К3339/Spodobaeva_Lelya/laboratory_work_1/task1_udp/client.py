import socket


HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 1024


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        message = "Hello, server"
        sock.sendto(message.encode("utf-8"), (HOST, PORT))
        print(f"Sent: {message}")

        response, address = sock.recvfrom(BUFFER_SIZE)
        print(f"Response from {address}: {response.decode('utf-8')}")


if __name__ == "__main__":
    main()

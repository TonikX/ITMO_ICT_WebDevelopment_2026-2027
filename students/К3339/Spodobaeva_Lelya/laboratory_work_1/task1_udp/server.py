import socket


HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 1024


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, PORT))
        print(f"UDP server started on {HOST}:{PORT}")

        message, address = sock.recvfrom(BUFFER_SIZE)
        print(f"Message from {address}: {message.decode('utf-8')}")

        response = "Hello, client"
        sock.sendto(response.encode("utf-8"), address)
        print("Response sent")


if __name__ == "__main__":
    main()

import socket

HOST = "127.0.0.1"  
PORT = 5000

def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    print(f"[SERVER] Listening on {HOST}:{PORT} (UDP)")

    data, client_address = server_socket.recvfrom(1024)
    message = data.decode()
    print(f"[SERVER] Received from {client_address}: {message}")

    reply = "Hello, client"
    server_socket.sendto(reply.encode(), client_address)
    print(f"[SERVER] Sent reply: {reply}")

    server_socket.close()

if __name__ == "__main__":
    main()

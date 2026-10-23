import socket

HOST = "127.0.0.1"
PORT = 5001

def compute_parallelogram_area(base: float, height: float) -> float:
    return base * height

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen(1)  # queue size of 1 pending connection
    print(f"[SERVER] Listening on {HOST}:{PORT} (TCP)")


    conn, addr = server_socket.accept()
    print(f"[SERVER] Connection established with {addr}")

    with conn:
        data = conn.recv(1024).decode()
        print(f"[SERVER] Received raw: {data}")

        base_str, height_str = data.split(",")
        base, height = float(base_str), float(height_str)

        area = compute_parallelogram_area(base, height)
        print(f"[SERVER] Computed area = {area}")

        conn.sendall(str(area).encode())

    server_socket.close()

if __name__ == "__main__":
    main()

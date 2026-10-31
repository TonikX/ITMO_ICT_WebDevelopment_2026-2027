import socket

ADDRESS = ("localhost", 5001)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(ADDRESS)
    print("UDP-сервер запущен на", ADDRESS)

    while True:
        data, address = sock.recvfrom(1024)
        print(f"Получено от {address}: {data.decode()}")
        sock.sendto("Hello, client".encode(), address)

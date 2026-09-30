import socket

ADDRESS = ("localhost", 5001)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.sendto("Hello, server".encode(), ADDRESS)
    data, _ = sock.recvfrom(1024)
    print(f"Ответ сервера: {data.decode()}")

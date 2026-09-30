import socket

SERVER = ('localhost', 8080)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    while True:
        message = input('Enter message: ')
        sock.sendto(message.encode(), SERVER)
        raw_data, address = sock.recvfrom(1024)
        print(f'Response from server: {raw_data.decode()}')
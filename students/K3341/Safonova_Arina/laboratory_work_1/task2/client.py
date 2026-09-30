import socket

base = input('Основание: ')
height = input('Высота: ')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect(('127.0.0.1', 8002))
    client_socket.sendall(f'{base} {height}\n'.encode('utf-8'))
    with client_socket.makefile('r', encoding='utf-8') as stream:
        print(stream.readline().strip())

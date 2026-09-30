import socket

print('Вычисление площади трапеции: S = (a + b) / 2 * h')
a = input('Основание a: ')
b = input('Основание b: ')
h = input('Высота h: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9001))

client_socket.sendall(f'{a};{b};{h}'.encode())

response = client_socket.recv(1024).decode()
print(f'Результат: {response}')

client_socket.close()

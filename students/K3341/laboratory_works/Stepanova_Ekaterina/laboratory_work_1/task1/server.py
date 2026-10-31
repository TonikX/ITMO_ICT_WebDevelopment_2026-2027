import socket

# создаем сокет
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# привязываем сокет к адресу и порту
server_sock.bind(('localhost', 8080))
print('Сервер запущен')

# принимаем сообщение от клиента
data, addr = server_sock.recvfrom(1024)
print(f"Сообщение от клиента:\n {data.decode('utf-8')}")
server_sock.sendto(b'Hello, client', addr)

server_sock.close()

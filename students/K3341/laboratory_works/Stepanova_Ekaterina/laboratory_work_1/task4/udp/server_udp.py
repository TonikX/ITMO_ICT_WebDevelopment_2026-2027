import socket

udp_server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# привяжем сокет к адресу и порту
udp_server_sock.bind(("localhost", 8080))
print("Сервер запущен.....")

# список, где сервер будет хранить пользователей
users = {}


def broadcast(message, addr):
    for add in users.keys():
        if add != addr:
            udp_server_sock.sendto(message.encode(), add)


while True:
    # ожидание данных от пользователей
    data, addr = udp_server_sock.recvfrom(1024)
    if addr not in users:
        users[addr] = data.decode()
        message = f"Пользователь {users[addr]} присоединился к чату"
        broadcast(message, addr)
    else:
        if data.decode() == '/exit':
            message = f'Пользователь {users[addr]} покинул чат'
            broadcast(message, addr)
            del users[addr]
        else:
            message = f"\n({users[addr]}): {data.decode()}"
            broadcast(message, addr)
            print(message)

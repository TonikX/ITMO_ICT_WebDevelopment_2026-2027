import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.sendto("Запрос клиента".encode(), ("127.0.0.1", 9001))

received, _ = udp_socket.recvfrom(1024)
print("Получено:", received.decode())
udp_socket.close()
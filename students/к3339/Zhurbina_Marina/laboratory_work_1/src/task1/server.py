import socket

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("127.0.0.1", 9001))

received, client_address = udp_socket.recvfrom(1024)
print("Принято:", received.decode())

udp_socket.sendto("Ответ сервера".encode(), client_address)
udp_socket.close()
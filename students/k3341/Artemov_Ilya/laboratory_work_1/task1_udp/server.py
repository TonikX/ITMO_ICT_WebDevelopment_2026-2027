import socket

HOST = "localhost"
PORT = 9001

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print(f"UDP-сервер запущен на {HOST}:{PORT}")

try:
    while True:
        data, client_address = server_socket.recvfrom(1024)
        print(f"Сообщение от клиента {client_address}: {data.decode()}")

        server_socket.sendto("Hello, client".encode(), client_address)
except KeyboardInterrupt:
    print("Сервер остановлен")
finally:
    server_socket.close()

import socket

HOST = '127.0.0.1'
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
    message = "Hello, server"
    print(f"[UDP Client] Отправка сообщения: {message}")

    client_socket.sendto(message.encode('utf-8'), (HOST, PORT))

    data, addr = client_socket.recvfrom(1024)
    print(f"[UDP Client] Получено от сервера: {data.decode('utf-8')}")

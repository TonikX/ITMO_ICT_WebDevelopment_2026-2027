import socket

HOST = '127.0.0.1'
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
    server_socket.bind((HOST, PORT))
    print(f"[UDP Server] Запущен на {HOST}:{PORT}")

    data, addr = server_socket.recvfrom(1024)
    print(f"[UDP Server] Получено от {addr}: {data.decode('utf-8')}")

    response = "Hello, client"
    server_socket.sendto(response.encode('utf-8'), addr)
    print(f"[UDP Server] Отправлен ответ: {response}")

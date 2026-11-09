import socket

HOST = '127.0.0.1'
PORT = 8081

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    print("[TCP Client] Подключено к серверу.")

    message = input("Введите основание и высоту параллелограмма через пробел (например, '3.06 7.23'): ")

    client_socket.sendall(message.encode('utf-8'))

    data = client_socket.recv(1024).decode('utf-8')
    print(f"[TCP Client] Ответ сервера: {data}")

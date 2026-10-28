import socket

HOST = '127.0.0.1'
PORT = 9090

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Отправляем сообщение серверу
    message = "Hello, server"
    client_socket.sendto(message.encode('utf-8'), (HOST, PORT))
    print(f"[Клиент] Отправлено: {message}")

    # Ждём ответ
    data, _ = client_socket.recvfrom(1024)
    response = data.decode('utf-8')
    print(f"[Клиент] Получено от сервера: {response}")

    client_socket.close()

if __name__ == '__main__':
    main()
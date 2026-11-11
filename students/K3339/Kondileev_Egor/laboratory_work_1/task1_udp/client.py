"""Задание 1: UDP-клиент."""
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 1024

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(5)
        message = "Hello, server"
        client.sendto(message.encode("utf-8"), (SERVER_HOST, SERVER_PORT))
        print(f"Отправлено серверу: {message}")

        try:
            data, server_address = client.recvfrom(BUFFER_SIZE)
            print(f"Ответ от {server_address}: {data.decode('utf-8')}")
        except socket.timeout:
            print("Ответ не получен за 5 секунд. Убедитесь, что сервер запущен.")

if __name__ == "__main__":
    main()

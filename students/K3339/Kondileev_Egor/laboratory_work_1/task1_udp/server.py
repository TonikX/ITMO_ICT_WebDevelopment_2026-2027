"""Задание 1: UDP-сервер."""
import socket

HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 1024

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((HOST, PORT))
        print(f"UDP-сервер запущен на {HOST}:{PORT}. Ожидаю сообщение...")
        data, client_address = server.recvfrom(BUFFER_SIZE)
        message = data.decode("utf-8")
        print(f"Получено от {client_address}: {message}")

        reply = "Hello, client"
        server.sendto(reply.encode("utf-8"), client_address)
        print(f"Отправлен ответ: {reply}")

if __name__ == "__main__":
    main()

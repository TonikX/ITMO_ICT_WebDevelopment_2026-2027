import socket

HOST = '127.0.0.1'
PORT = 9090

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"[Сервер] Запущен на {HOST}:{PORT}, ждём сообщения...")

    while True:
        # Получаем данные и адрес клиента
        data, client_address = server_socket.recvfrom(1024)
        message = data.decode('utf-8')
        print(f"[Сервер] Получено от {client_address}: {message}")

        response = "Hello, client"
        server_socket.sendto(response.encode('utf-8'), client_address)
        print(f"[Сервер] Отправлено: {response}")

if __name__ == '__main__':
    main()
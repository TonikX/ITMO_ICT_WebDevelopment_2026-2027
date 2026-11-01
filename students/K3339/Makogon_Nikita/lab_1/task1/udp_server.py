import socket

HOST = '127.0.0.1'
PORT = 8081

def run_udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"[UDP СЕРВЕР] Запущен на {HOST}:{PORT}")

    try:
        while True:
            data, client_address = server_socket.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"[UDP] Получено от {client_address}: {message}")

            if message == "Hello, server":
                response = "Hello, client"
                server_socket.sendto(response.encode('utf-8'), client_address)
                print(f"[UDP] Отправлен ответ клиенту {client_address}: {response}")
    except KeyboardInterrupt:
        print("\n[UDP СЕРВЕР] Остановлен.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_udp_server()
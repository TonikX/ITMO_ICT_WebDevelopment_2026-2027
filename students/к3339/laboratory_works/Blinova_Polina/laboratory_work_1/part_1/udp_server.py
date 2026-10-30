import socket

def run_udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_address = ('localhost', 12345)
    server_socket.bind(server_address)
    
    print("UDP Сервер запущен на порту 12345")
    print("Ожидание сообщений...")
    
    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"Получено сообщение от {client_address}: {message}")
            
            response = "Hello, client"
            server_socket.sendto(response.encode('utf-8'), client_address)
            print(f"Отправлен ответ: {response}")
            
        except KeyboardInterrupt:
            print("\nСервер остановлен")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            continue
    
    server_socket.close()

if __name__ == "__main__":
    run_udp_server()
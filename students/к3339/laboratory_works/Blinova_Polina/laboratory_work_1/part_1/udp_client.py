import socket

def run_udp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_address = ('localhost', 12345)
    
    try:
        message = "Hello, server"
        print(f"Отправка: {message}")
        client_socket.sendto(message.encode('utf-8'), server_address)
        
        data, server = client_socket.recvfrom(1024)
        response = data.decode('utf-8')
        print(f"Получен ответ: {response}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    run_udp_client()